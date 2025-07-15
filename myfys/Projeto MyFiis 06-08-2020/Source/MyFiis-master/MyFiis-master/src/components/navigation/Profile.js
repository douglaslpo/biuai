import React, { Component } from "react";
import { View, Text, StyleSheet, TextInput } from "react-native";
import Header from "./Header";
import SmallRoundedSaveButton from "../../components/common/buttons/SmallRoundedSaveButton";
import { withFirebase } from "../../components/firebase";

class Profile extends Component {
  constructor(props) {
    super(props);

    let userName = "Não cadastrado";
    let email = "Sem informação do E-mail";
    let currentUser = this.props.firebase.auth.currentUser;

    if (currentUser) {
      if (currentUser.displayName) {
        userName = currentUser.displayName;
      }

      if (currentUser.email) {
        email = currentUser.email;
      }
    }

    this.state = {
      editing: false,

      originalName: userName,
      originalEmail: email,

      userName: userName,
      email: email,

      currentUser: currentUser,
    };
  }

  enableEdit() {
    this.setState({
      editing: true,
    });
  }

  onChangeName(e) {
    this.setState({
      userName: e,
    });
  }

  onChangeEmail(e) {
    this.setState({
      email: e,
    });
  }


  save() {
    let name = this.state.userName;
    let email = this.state.email;

    if (name == "" || email == "") {
      return;
    }

    if (name != this.state.originalName) {
      this.props.firebase.auth.currentUser
        .updateProfile({
          displayName: name,
        })
        .then(function () {

        })
        .catch(function (e) {
          console.log(e);
          alert('Houve um erro ao editar o seu nome. Tente novamente mais tarde.');
        });
    }

    if (email != this.state.originalEmail) {
      this.props.firebase.auth.currentUser
        .updateEmail(email)
        .then(
          function () {

          }
        )
        .catch(function (error) {
          console.log(error);
          if (error.code == "auth/requires-recent-login") {
            alert(
              "Houve um erro ao tentar alterar o seu e-mail. A ação de alteração de e-mail requer que você se deslogue do aplicativo e logue novamente."
            );
          } else if (error.code == "auth/email-already-in-use") {
            alert(
              "Houve um erro ao tentar alterar o seu e-mail. Este e-mail já está em uso."
            );
          } else {
            alert('Houve um erro ao editar o seu E-mail. Tente novamente mais tarde.');
          }
        });
    }

    this.setState({
      editing: false
    });
  }

  render() {
    const inputName = () => {
      if (this.state.editing) {
        return (
          <TextInput
            style={styles.textInput}
            value={this.state.userName}
            onChangeText={this.onChangeName.bind(this)}
            placeholder="Nome"
          />
        );
      } else {
        return <Text style={styles.info}>{this.state.userName}</Text>;
      }
    };

    const inputEmail = () => {
      if (this.state.editing) {
        return (
          <TextInput
            style={styles.textInput}
            value={this.state.email}
            onChangeText={this.onChangeEmail.bind(this)}
            placeholder="E-mail"
            keyboardType="email-address"
            textContentType="emailAddress"
          />
        );
      } else {
        return <Text style={styles.info}>{this.state.email}</Text>;
      }
    };

    const currentButton = () => {
      if (this.state.editing) {
        return (
          <SmallRoundedSaveButton
            onPress={() => this.save()}
            loading={false}
            text="Salvar"
          />
        );
      } else {
        return (
          <SmallRoundedSaveButton
            loading={false}
            text="Editar"
            onPress={() => this.enableEdit()}
          />
        );
      }
    };

    return (
      <View style={styles.container}>
        <Header
          title="Perfil"
          style={styles.header}
          onPress={() => {
            this.props.setScreen("sidemenu");
          }}
        />

        <View style={styles.subContainer}>
          <Text style={styles.title}>DETALHES DO PERFIL</Text>

          <View style={styles.view}>
            <Text style={styles.subtitle}>Nome</Text>
            {inputName()}
          </View>

          <View style={styles.view}>
            <Text style={styles.subtitle}>Email</Text>
            {inputEmail()}
          </View>

          <View style={styles.horizontalRow}></View>

          {/* <Text style={styles.title}>DETALHES DE SEGURANÇA</Text>

          <View style={styles.view}>
            <Text style={styles.subtitle}>Senha</Text>

            <Text style={styles.textInput} onPress={() => console.log("ok")}>
              Mudar senha
            </Text>
          </View>

          <View style={{ marginBottom: 100 }}></View> */}

          {currentButton()}
        </View>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 20,
    backgroundColor: "#1EBEA5",
  },

  header: {
    marginTop: 30
  },

  subContainer: {
    flex: 1,
    paddingTop: 50,
    backgroundColor: "#1EBEA5",
  },

  title: {
    color: "#FAFAFA",
  },

  subtitle: {
    color: "#FAFAFA",
    fontWeight: "bold",
    fontSize: 14,
    fontFamily: "Montserrat-Regular",
    fontStyle: "normal",
  },

  info: {
    color: "#FAFAFA",
    fontWeight: "300",
    fontSize: 14,
    fontFamily: "Montserrat-Regular",
    fontStyle: "normal",
  },

  view: {
    marginTop: 10,
    marginBottom: 10,
  },

  horizontalRow: {
    marginTop: 20,
    marginBottom: 20,
    borderWidth: 0.5,
    borderColor: "#CCCDD1",
  },

  touchableOpacity: {
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "white",
    borderRadius: 100,
    alignSelf: "center",
    width: 150,
    height: 100,
    maxHeight: 30,
  },
  text: {
    alignSelf: "center",
    paddingLeft: 50,
    paddingRight: 50,
    paddingTop: 15,
    paddingBottom: 15,
    color: "#26BFBD",
    fontSize: 14,
  },
  spinner: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },

  touchableOpacity: {
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "white",
    borderRadius: 100,
    alignSelf: "center",
    width: 150,
    height: 100,
    maxHeight: 30,
  },
  text: {
    alignSelf: "center",
    paddingLeft: 50,
    paddingRight: 50,
    paddingTop: 15,
    paddingBottom: 15,
    color: "#26BFBD",
    fontSize: 14,
  },
  spinner: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },

  textInput: {
    color: "#26BFBD",
    backgroundColor: "#FFFF",
    borderRadius: 30,
    paddingLeft: 15,
    paddingVertical: 5,
  },
});

export default withFirebase(Profile);
