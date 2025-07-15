import React from "react";
import {
  View,
  StyleSheet,
  Text,
  KeyboardAvoidingView,
  ScrollView,
  TouchableOpacity,
  Linking,
} from "react-native";
import RoundedInput from "../../components/common/inputs/RoundedInput";
import LargeRoundedButton from "../../components/common/buttons/LargeRoundedButton";
import Link from "../../components/common/buttons/Link";
import Spinner from "../../components/login/LoginForm/Spinner";
import AwesomeAlert from "react-native-awesome-alerts";

import { withFirebase } from "../../components/firebase";
import ScreenHeader from "../../components/common/ScreenHeader";
import MainHeader from "../../components/common/MainHeader";
import { CommonActions } from "@react-navigation/native";

class NewUserScreen extends React.Component {
  static navigationOptions = {
    drawerLabel: "Cadastro",
  };

  state = {
    email: "",
    password: "",
    name: "",
    loading: false,
    showAlert: false,
    errorCode: null,
    errorTitle: "",
    errorMessage: "",
    canSubmit: false,
  };

  async createNewUser() {
    if (!this.state.email) {
      this.setState({
        showAlert: true,
        errorTitle: "E-mail obrigatório",
        errorMessage:
          "Você deve preencher o campo 'E-mail' para conseguir se cadastrar no MyFiis",
      });
      return;
    }

    if (!this.state.password) {
      this.setState({
        showAlert: true,
        errorTitle: "Senha obrigatória",
        errorMessage:
          "Você deve preencher o campo 'Senha' para conseguir se cadastrar no MyFiis",
      });
      return;
    }

    this.setState({ loading: true });

    try {
      let authUser = await this.props.firebase.createUserWithEmailAndPassword(
        this.state.email,
        this.state.password
      );

      try {
        await this.props.firebase.updateProfile({
          displayName: this.state.name,
        });
      } catch (error) {
        console.log("error on update updateProfile", error);
      }

      this.setState({ loading: false }, () => {
        this.props.navigation.dispatch(
          CommonActions.reset({
            index: 1,
            routes: [{ name: "UserArea" }],
          })
        );
      });
    } catch (error) {
      this.handleErrorCode(error.code);
      this.setState({ loading: false });
    }
  }

  handleErrorCode(errorCode) {
    switch (errorCode) {
      case "auth/email-already-in-use":
        this.setState({
          errorCode: errorCode,
          errorTitle: "E-mail já utilizado",
          errorMessage:
            "Que pena! Este E-mail já está em uso no MyFiis. Escolha um outro E-mail de sua preferência!",
          showAlert: true,
        });
        break;

      case "auth/weak-password":
        this.setState({
          errorCode: errorCode,
          errorTitle: "Senha fraca",
          errorMessage:
            "Que pena! A sua senha deve conter pelo menos 6 caracteres.",
          showAlert: true,
        });
        break;

      case "auth/invalid-email":
        this.setState({
          errorCode: errorCode,
          errorTitle: "E-mail inválido",
          errorMessage:
            "Que pena! O E-mail inserido não está nos padrões aceitos pelo MyFiis. Por favor, escolha outro E-mail e tente novamente.",
          showAlert: true,
        });
        break;
      default:
        this.setState({
          errorCode: errorCode,
          errorTitle: "Erro",
          errorMessage:
            "Que pena! Ocorreu um erro inesperado ao cadastrar. Contate o nosso suporte.",
          showAlert: true,
        });
        break;
    }
  }

  showAlert() {
    this.setState({ showAlert: true });
  }

  hideAlert() {
    this.setState({ showAlert: false });
  }

  onChangeEmail(e) {
    this.setState({ email: e }, () => {
      this.checkCanSubmit();
    });
  }

  onChangePassword(e) {
    this.setState({ password: e }, () => {
      this.checkCanSubmit();
    });
  }

  onChangeName(e) {
    this.setState({ name: e }, () => {
      this.checkCanSubmit();
    });
  }

  checkCanSubmit() {
    if (this.state.email && this.state.password && this.state.name) {
      this.setState({
        canSubmit: true,
      });
    } else {
      this.setState({
        canSubmit: false,
      });
    }
  }

  renderButton() {
    if (this.state.loading) {
      return <Spinner size="large" />;
    }

    return (
      <LargeRoundedButton
        disabled={!this.state.canSubmit}
        text="Cadastrar"
        onPress={this.createNewUser.bind(this)}
      />
    );
  }

  render() {
    const { showAlert, errorMessage, errorTitle } = this.state;

    return (
      <>
        <MainHeader />

        <ScrollView style={{ backgroundColor: "#FAFAFA" }}>
          <View style={styles.container}>
            <ScreenHeader title="Cadastro" navigation={this.props.navigation} />
            <RoundedInput
              label="Nome"
              style={{ height: 25 }}
              value={this.state.name}
              onChange={this.onChangeName.bind(this)}
              autofocus
              placeholder="Primeiro e último nome *"
            />
            <RoundedInput
              label="Email"
              value={this.state.email}
              autoCompleteType="email"
              autoCorrect={false}
              keyboardType="email-address"
              onChange={this.onChangeEmail.bind(this)}
              placeholder="Email *"
            />
            <RoundedInput
              label="Senha"
              value={this.state.password}
              secureTextEntry
              onChange={this.onChangePassword.bind(this)}
              placeholder="Senha *"
            />

            <View style={styles.terms}>
              <TouchableOpacity
                onPress={() =>
                  Linking.openURL(
                    "https://drive.google.com/file/d/18TweMfAuJLqpaSlPxb1rB2-cx5WaT2r-/view?usp=sharing"
                  )
                }
              >
                <Text
                  textAlign="justify"
                  opacity={0.5}
                  style={styles.termsText}
                >
                  Ao continuar, você concorda com a{" "}
                  <Text opacity={1} style={styles.terms1}>
                    Política de Privacidade.
                  </Text>
                </Text>
              </TouchableOpacity>
            </View>
            {this.renderButton()}
            <View style={styles.hasAccount}>
              <Text style={styles.message}>Já possui uma conta?</Text>
              <Link
                text="Entrar"
                to="Login"
                navigation={this.props.navigation}
              />
            </View>
            <AwesomeAlert
              show={showAlert}
              showProgress={false}
              title={errorTitle}
              message={errorMessage}
              closeOnTouchOutside={true}
              closeOnHardwareBackPress={false}
              showCancelButton={false}
              showConfirmButton={true}
              confirmText="Ok"
              confirmButtonColor="#DD6B55"
              onCancelPressed={() => {
                this.hideAlert();
              }}
              onConfirmPressed={() => {
                this.hideAlert();
              }}
              confirmButtonStyle={styles.confirmButtonColor}
            />
          </View>
        </ScrollView>
      </>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 25,
    width: "100%",
  },

  message: {
    fontSize: 13,
    marginRight: 10,
  },

  hasAccount: {
    marginTop: 20,
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "flex-start",
    marginBottom: 10,
  },

  viewError: {
    marginTop: 10,
    justifyContent: "center",
    textAlign: "center",
    maxWidth: 300,
    borderColor: "black",
  },

  textError: {
    color: "red",
    fontSize: 12,
  },

  confirmButtonColor: {
    backgroundColor: "rgba(58, 176, 162, 0.5)",
  },

  keyboardAvoidingView: {
    width: "100%",
  },

  terms: {
    flex: 1,
    marginTop: 20,
  },

  termsText: {
    color: "rgba(24, 24, 24, 0.5)",
  },

  terms1: {
    color: "#181818",
    fontWeight: "bold",
  },

  terms2: {
    color: "#181818",
    fontWeight: "bold",
  },
});

export default withFirebase(NewUserScreen);
