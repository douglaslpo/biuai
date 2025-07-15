import React from "react";
import { View, StyleSheet, Text, FlatList } from "react-native";
import FiiData from "../../components/wallet/FiiData";
import Details from "../../components/wallet/Details";
import HorizontalRow from "../../components/wallet/HorizontalRow";
import ActionButton from "../../components/common/buttons/ActionButton";
import ScreenHeader from "../../components/common/ScreenHeader";
import MainHeader from "../../components/common/MainHeader";
import Spinner from "../../components/login/LoginForm/Spinner";
import { withFirebase } from "../../components/firebase";
import Pill from "../../components/wallet/Pill";
import Action from "../../components/wallet/Action";

class WalletScreen extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      fiisList: [],
      selectedFii: null,
      loading: true,
      userApplications: [],
      userDividends: [],
      fiiValueInfo: null,
    };
  }

  async componentDidMount() {
    this.unsubscribeFocusListener = this.props.navigation.addListener(
      "focus",
      () => {
        this.loadWalletFiis();
      }
    );
  }

  componentWillUnmount() {
    this.unsubscribeFocusListener();
  }

  async loadWalletFiis() {
    try {
      let screenFiis = [];

      let apps = await this.props.firebase.getApplications();
      let dividends = await this.props.firebase.getDividends();

      let distinctApps = {};

      for (let i = 0; i < apps.length; i++) {
        let code = apps[i].fii;
        if (distinctApps[code]) continue;

        distinctApps[code] = code;
      }

      for (let i = 0; i < dividends.length; i++) {
        let code = dividends[i].fii;
        if (distinctApps[code]) continue;

        distinctApps[code] = code;
      }

      let allFiis = this.props.firebase.database.fiis;

      for (const key in distinctApps) {
        let fiiFound = null;
        let appFii = allFiis.filter((objFii) => objFii.code === key);

        if (appFii.length > 0) fiiFound = appFii[0];

        if (!fiiFound) {
          fiiFound = {
            code: key,
            name: "",
            segment: "",
            manager: "",
          };
        }

        screenFiis.push(fiiFound);
      }

      let newSelectedFii = this.state.selectedFii;

      //Verificar se o fundo que estava selecionado ainda existe
      if (
        this.state.selectedFii != null &&
        screenFiis.filter((sfii) => sfii.code == this.state.selectedFii.code)
          .length == 0
      )
        newSelectedFii = null;

      if (newSelectedFii == null) {
        newSelectedFii = screenFiis.length > 0 ? screenFiis[0] : null;
      }

      this.setState(
        {
          fiisList: screenFiis,
          loading: false,
          selectedFii: newSelectedFii,
          userApplications: apps,
          userDividends: dividends,
        },
        this.loadSelectedFiiValueInfo
      );
    } catch (e) {
      console.log("Error on loadWalletFiis", e);
    }
  }

  async getAppAveragePrice(fiiCode) {
    let sumValue = 0;
    let quantity = 0;
    try {
      for (let i = 0; i < this.state.userApplications.length; i++) {
        const app = this.state.userApplications[i];

        if (fiiCode != app.fii) continue;

        quantity += app.quantity;
        sumValue += app.price * app.quantity;
      }
    } catch (e) {
      console.log(e);
    }

    return quantity > 0 ? sumValue / 100 / quantity : 0;
  }

  async calcProfitability(fiiCode) {
    let averagePrice = await this.getAppAveragePrice(fiiCode);

    let sumProfit = 0;
    let averageProfit = 0;
    let quantityDividends = 0;

    for (let i = 0; i < this.state.userDividends.length; i++) {
      const dividend = this.state.userDividends[i];

      if (fiiCode != dividend.fii) continue;

      sumProfit += dividend.total / 100 / dividend.quantity;

      quantityDividends++;
    }

    if (averagePrice > 0 && sumProfit > 0) {
      averageProfit = ((sumProfit / quantityDividends) * 100) / averagePrice;
    }

    return averageProfit;
  }

  async loadSelectedFiiValueInfo() {
    let quantity = 0;
    let totalApplied = 0;
    let totalReceived = 0;
    let profitability = 0;

    if (this.state.selectedFii == null) return;

    try {
      for (let i = 0; i < this.state.userApplications.length; i++) {
        const app = this.state.userApplications[i];
        if (app.fii === this.state.selectedFii.code) {
          quantity += app.quantity;
          totalApplied += app.quantity * app.price;
        }
      }

      for (let i = 0; i < this.state.userDividends.length; i++) {
        const dividend = this.state.userDividends[i];
        if (dividend.fii === this.state.selectedFii.code) {
          totalReceived += dividend.total;
        }
      }

      profitability = await this.calcProfitability(this.state.selectedFii.code);
    } catch (e) {
      console.log("Error on loadSelectedFiiValueInfo", e);
    }

    this.setState({
      fiiValueInfo: {
        quantity: quantity,
        totalApplied: totalApplied,
        totalReceived: totalReceived,
        profitability: profitability,
      },
    });
  }

  onSelectFii(fii) {
    if (fii.code === this.state.selectedFii.code) return;

    this.setState({ selectedFii: fii }, this.loadSelectedFiiValueInfo);
  }

  renderFiisList() {
    if (this.state.fiisList.length === 0) {
      return (
        <View style={styles.notFoundView}>
          <Text style={styles.notFound}>
            Nenhum fundo foi encontrado em sua carteira. Adicione pelo menos um
            fundo à sua carteira para aparecer aqui.
          </Text>
        </View>
      );
    }

    return (
      <View style={{ flex: 1, maxHeight: 40 }}>
        <FlatList
          showsHorizontalScrollIndicator={false}
          horizontal={true}
          data={this.state.fiisList}
          ListEmptyComponent={() => {
            return <View></View>;
          }}
          keyExtractor={(item) => item.code}
          renderItem={({ item }) => {
            return (
              <Pill
                fii={item}
                selected={
                  this.state.selectedFii &&
                  this.state.selectedFii.code === item.code
                }
                onSelectFii={this.onSelectFii.bind(this)}
              />
            );
          }}
        />
      </View>
    );
  }

  render() {
    if (this.state.loading) {
      return (
        <View
          style={{ flex: 1, alignItems: "center", justifyContent: "center" }}
        >
          <Spinner size="large" />
        </View>
      );
    }

    return (
      <>
        <View style={styles.container}>
          <MainHeader navigation={this.props.navigation} />
          <ScreenHeader title="Sua Carteira" />

          {this.renderFiisList()}

          {this.state.fiisList.length ? (
            <>
              <FiiData
                fii={this.state.selectedFii ? this.state.selectedFii : {}}
              />

              <HorizontalRow />

              {this.state.fiiValueInfo ? (
                <Details data={this.state.fiiValueInfo} />
              ) : null}

              <View style={styles.actionsContainer}>
                <View style={styles.actionsRow}>
                  <Action
                    text="Aplicações"
                    onPress={() =>
                      this.props.navigation.navigate("Applications", {
                        fiiScope: this.state.selectedFii.code,
                      })
                    }
                  />

                  <Action
                    text="Div. Recebidos"
                    onPress={() =>
                      this.props.navigation.navigate("Dividends", {
                        fiiScope: this.state.selectedFii.code,
                      })
                    }
                  />
                </View>
                <View style={styles.fakeRow}></View>
                <View style={styles.fakeRow}></View>
              </View>
            </>
          ) : null}
        </View>

        <ActionButton />
      </>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#FAFAFA",
  },

  notFoundView: {
    flex: 1,
    alignSelf: "center",
    justifyContent: "center",
  },

  notFound: {
    flex: 1,
    marginLeft: 10,
    alignSelf: "center",
  },

  actionsContainer: {
    justifyContent: "flex-start",
    flex: 2,
  },

  actionsRow: {
    flex: 1,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginHorizontal: 14,
  },

  fakeRow: {
    flex: 1,
  },
});

export default withFirebase(WalletScreen);
