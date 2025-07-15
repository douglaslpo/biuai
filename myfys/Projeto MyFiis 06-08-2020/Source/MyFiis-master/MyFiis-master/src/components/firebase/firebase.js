import auth from "@react-native-firebase/auth";
import firestore from "@react-native-firebase/firestore";
import PREDEFINEDFIIS from "../../lib/fiis";
import AsyncStorage from "@react-native-community/async-storage";

const fiisListTimestamp = 1592770957;

class Firebase {
  constructor() {
    this.auth = auth();
    this.firestore = firestore();
    this.database = {
      fiis: [],
    };

    this.syncChecked = false;
    this.fiisListLoaded = false;
  }

  loadFiisList = async function () {
    if (this.fiisListLoaded) return;

    this.fiisListLoaded = true;

    let newFiisList = false;
    let updateFiisList = false;
    let fiisList = null;
    let checkLastFiiListUpdate = fiisListTimestamp;

    try {
      const storedFiisList = await AsyncStorage.getItem("@fiisList");

      const lastFiiListUpdate = await AsyncStorage.getItem(
        "@lastFiiListUpdate"
      );

      if (lastFiiListUpdate !== null)
        checkLastFiiListUpdate = Number(lastFiiListUpdate);

      if (storedFiisList !== null) {
        fiisList = JSON.parse(storedFiisList);
      } else {
        fiisList = PREDEFINEDFIIS;
        newFiisList = true;
      }
    } catch (e) {
      console.log("error on loadNewFiis", e);
    }

    try {
      await this.firestore.enableNetwork();

      let querySnapshot = null;
      //Se acontecer de dar erro tenta novamente
      for (let i = 0; i < 5; i++) {
        try {
          if (i > 0)
            await new Promise((resolve) => {
              setTimeout(resolve, 200);
            });

          querySnapshot = await this.firestore
            .collection("fiis")
            .where("updated_at", ">=", checkLastFiiListUpdate)
            .get({ source: "server" }); //Force get from cloud

          break;
        } catch (e) {
          console.log("error from cloud: ", e);
        }
      }

      //console.log(checkLastFiiListUpdate, " check in cloud timestamp");
      //console.log("snapshot size", querySnapshot.size);
      //console.log("metadata from cache", querySnapshot.metadata.fromCache);

      let fiisToRemove = [];

      querySnapshot.forEach((documentSnapshot) => {
        let documentData = documentSnapshot.data();
        let lFound = false;

        //Colocar tudo como maisculo para evitar problemas de comparação
        documentData.code = documentData.code.toUpperCase();

        //console.log(checkLastFiiListUpdate, "from cloud", documentData);

        updateFiisList = true; //Houve alguma alteração

        if (fiisList !== null) {
          for (let i = 0; i < fiisList.length; i++) {
            if (fiisList[i].code == documentData.code) {
              if (documentData.inactive === true) {
                fiisToRemove.push(documentData.code); //Remoção
              } else {
                fiisList[i] = documentData; //Alteracão normal
              }

              lFound = true;
              break;
            }
          }

          if (!lFound) fiisList.push(documentData);
        }
      });

      //Remover fundos
      for (let i = 0; i < fiisToRemove.length; i++) {
        for (let j = 0; j < fiisList.length; j++) {
          if (fiisToRemove[i] == fiisList[j].code) {
            fiisList.splice(j, 1); //Remoção
            break;
          }
        }
      }
    } catch (e) {
      console.log("error on get new fiis", e, e.code);
    }

    if (fiisList != null) this.database.fiis = fiisList;

    try {
      if (fiisList != null && (updateFiisList || newFiisList)) {
        await AsyncStorage.setItem("@fiisList", JSON.stringify(fiisList));

        let now = new Date();
        let utc_timestamp = Date.UTC(
          now.getUTCFullYear(),
          now.getUTCMonth(),
          now.getUTCDate(),
          now.getUTCHours(),
          now.getUTCMinutes(),
          now.getUTCSeconds(),
          now.getUTCMilliseconds()
        );
        utc_timestamp = Math.trunc(utc_timestamp / 1000);

        await AsyncStorage.setItem(
          "@lastFiiListUpdate",
          utc_timestamp.toString()
        );
      }
    } catch (e) {
      console.log("error on store fiislist", e);
    }
  };

  //The settings() method must be called before any Firestore interaction is performed, otherwise it will only take effect on the next app launch
  settings = async function () {
    try {
      //Persistence is enabled by default
      //Config cache to unlimited
      await this.firestore.settings({
        cacheSizeBytes: firestore.CACHE_SIZE_UNLIMITED,
      });
    } catch (e) {
      console.log("Error on firebase settings", e);
    }
  };

  //Verificar se o aplicativo já sincronizou seus dados do local storage com o cloud storage. Se ainda nao, busca todos os dados do usuário do cloud.
  dataSync = async function () {
    try {
      if (!(this.auth && this.auth.currentUser)) return;

      if (this.syncChecked) return;

      this.syncChecked = true;

      let checkDataSync = async function () {
        let documentSnapshot = null;

        try {
          documentSnapshot = await this.firestore
            .collection("datasync")
            .doc(this.auth.currentUser.uid)
            .get();

          return documentSnapshot ? documentSnapshot.exists : false;
        } catch (e) {}
        return documentSnapshot;
      }.bind(this);

      let loadApplications = async function () {
        return this.firestore
          .collection("wallet")
          .doc(this.auth.currentUser.uid)
          .collection("applications")
          .get();
      }.bind(this);

      let loadDividends = async function () {
        return this.firestore
          .collection("wallet")
          .doc(this.auth.currentUser.uid)
          .collection("dividends")
          .get();
      }.bind(this);

      await this.firestore.disableNetwork();

      if (await checkDataSync()) return await this.firestore.enableNetwork();

      let apps = await loadApplications(); //Try from cache
      let dividends = await loadDividends(); //Try from cache

      await this.firestore.enableNetwork();

      if (apps["_docs"] && apps["_docs"].length == 0) await loadApplications(); //Get From Cloud

      if (dividends["_docs"] && dividends["_docs"].length == 0)
        await loadDividends(); //Get From Cloud

      //Try from cloud
      if (!(await checkDataSync())) {
        try {
          await this.firestore
            .collection("datasync")
            .doc(this.auth.currentUser.uid)
            .set({ user_id: this.auth.currentUser.uid });
        } catch (e) {
          console.log("error on add datasync", e);
        }
      }
    } catch (e) {
      console.log("error on datasync", e);
      await this.firestore.enableNetwork();
    }
  };

  loadInitialData = async function () {
    try {
      let querySnapshot = await this.firestore.collection("fiis").get();

      querySnapshot.forEach((documentSnapshot) => {
        this.database.fiis.push(documentSnapshot.data());
      });

      //console.log("load loadInitialData fiis", this.database.fiis);
    } catch (e) {
      console.log("firestore loadInitialData", e);
    }
  };

  getApplications = async function (filters = {}) {
    try {
      let apps = [];

      //Load from cache
      await this.firestore.disableNetwork();

      let querySnapshot = null;

      if (
        filters.period &&
        filters.period.start &&
        filters.period.end &&
        filters.fiiCode
      ) {
        querySnapshot = await this.firestore
          .collection("wallet")
          .doc(this.auth.currentUser.uid)
          .collection("applications")
          .where("fii", "==", filters.fiiCode)
          .where("date", ">=", filters.period.start)
          .where("date", "<=", filters.period.end)
          .orderBy("date", "desc")
          .get();
      } else if (filters.fiiCode) {
        querySnapshot = await this.firestore
          .collection("wallet")
          .doc(this.auth.currentUser.uid)
          .collection("applications")
          .where("fii", "==", filters.fiiCode)
          .orderBy("date", "desc")
          .get();
      } else {
        querySnapshot = await this.firestore
          .collection("wallet")
          .doc(this.auth.currentUser.uid)
          .collection("applications")
          .orderBy("date", "desc")
          .get();
      }

      //Adicionar paginação depois, quando rolar o scroll
      querySnapshot.forEach((documentSnapshot) => {
        let data = documentSnapshot.data();
        data.id = documentSnapshot.id;
        apps.push(data);
      });

      await this.firestore.enableNetwork();

      return apps;
    } catch (e) {
      console.log("firestore getApplications", e);
      await this.firestore.enableNetwork();
    }
  };

  addApplication = async function (data) {
    try {
      let result = await this.firestore
        .collection("wallet")
        .doc(this.auth.currentUser.uid)
        .collection("applications")
        .add({
          ...{ user_id: this.auth.currentUser.uid },
          ...data,
        });
    } catch (e) {
      console.log("firestore addApplication", e);
    }
  };

  updateApplication = async function (data) {
    try {
      await this.firestore
        .collection("wallet")
        .doc(this.auth.currentUser.uid)
        .collection("applications")
        .doc(data.id)
        .set({ ...{ user_id: this.auth.currentUser.uid }, ...data.data });
    } catch (e) {
      console.log("firestore updateApplication", e);
    }
  };

  deleteApplication = async function (data) {
    try {
      await this.firestore
        .collection("wallet")
        .doc(this.auth.currentUser.uid)
        .collection("applications")
        .doc(data.id)
        .delete();
    } catch (e) {
      console.log("firestore deleteApplication", e);
    }
  };

  getDividends = async function (filters = {}) {
    try {
      let dividends = [];

      //Load from cache
      await this.firestore.disableNetwork();

      let querySnapshot = null;

      if (
        filters.period &&
        filters.period.start &&
        filters.period.end &&
        filters.fiiCode
      ) {
        querySnapshot = await this.firestore
          .collection("wallet")
          .doc(this.auth.currentUser.uid)
          .collection("dividends")
          .where("fii", "==", filters.fiiCode)
          .where("date", ">=", filters.period.start)
          .where("date", "<=", filters.period.end)
          .orderBy("date", "desc")
          .get();
      } else if (filters.fiiCode) {
        querySnapshot = await this.firestore
          .collection("wallet")
          .doc(this.auth.currentUser.uid)
          .collection("dividends")
          .where("fii", "==", filters.fiiCode)
          .orderBy("date", "desc")
          .get();
      } else {
        querySnapshot = await this.firestore
          .collection("wallet")
          .doc(this.auth.currentUser.uid)
          .collection("dividends")
          .orderBy("date", "desc")
          .get();
      }

      //Adicionar paginação depois, quando rolar o scroll
      querySnapshot.forEach((documentSnapshot) => {
        let data = documentSnapshot.data();
        data.id = documentSnapshot.id;
        dividends.push(data);
      });

      await this.firestore.enableNetwork();

      return dividends;
    } catch (e) {
      console.log("firestore getDividends", e);
      await this.firestore.enableNetwork();
    }
  };

  addDividend = async function (data) {
    try {
      let result = await this.firestore
        .collection("wallet")
        .doc(this.auth.currentUser.uid)
        .collection("dividends")
        .add({
          ...{ user_id: this.auth.currentUser.uid },
          ...data,
        });
    } catch (e) {
      console.log("firestore addDividend", e);
    }
  };

  updateDividend = async function (data) {
    try {
      await this.firestore
        .collection("wallet")
        .doc(this.auth.currentUser.uid)
        .collection("dividends")
        .doc(data.id)
        .set({ ...{ user_id: this.auth.currentUser.uid }, ...data.data });
    } catch (e) {
      console.log("firestore updateDividend", e);
    }
  };

  deleteDividend = async function (data) {
    try {
      await this.firestore
        .collection("wallet")
        .doc(this.auth.currentUser.uid)
        .collection("dividends")
        .doc(data.id)
        .delete();
    } catch (e) {
      console.log("firestore deleteDividend", e);
    }
  };

  importFiis = async function () {
    /*
            try
            {
                for(let i = 0; i < fiis.length; i++)
                {
                    console.log("import ", fiis[i].code);
                    await this.firestore.collection("fiis").doc(fiis[i].code).set(fiis[i]);
                }
            }
            catch(e)
            {
                console.log("importFiis", e);
            }
            */
  };

  getInTouch = async function (data) {
    try {
      if (this.auth.currentUser) {
        data.email = this.auth.currentUser.email
          ? this.auth.currentUser.email
          : "";
        data.name = this.auth.currentUser.displayName
          ? this.auth.currentUser.displayName
          : "";
      }

      await this.firestore.collection("contacts").add(data);
      return true;
    } catch (e) {
      console.log("firestore contacts");
    }
  };

  createUserWithEmailAndPassword = (email, password) =>
    this.auth.createUserWithEmailAndPassword(email, password);

  signInWithEmailAndPassword = (email, password) =>
    this.auth.signInWithEmailAndPassword(email, password);

  signOut = () => this.auth.signOut();

  passwordReset = (email) => this.auth.sendPasswordResetEmail(email);

  passwordUpdate = (password) => this.auth.currentUser.updatePassword(password);

  onAuthStateChanged = (callback) => this.auth.onAuthStateChanged(callback);

  updateProfile = (obj) => this.auth.currentUser.updateProfile(obj);

  getUserEmail = () => {
    if (this.auth && this.auth.currentUser) {
      return this.auth.currentUser.email;
    } else {
      return null;
    }
  };

  getUsername = () => {
    if (
      this.auth &&
      this.auth.currentUser &&
      this.auth.currentUser.displayName
    ) {
      return this.auth.currentUser.displayName;
    } else {
      return null;
    }
  };
}

export default Firebase;
