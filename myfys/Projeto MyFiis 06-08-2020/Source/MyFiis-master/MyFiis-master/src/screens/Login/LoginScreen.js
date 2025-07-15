import React from "react";
import {
  Text,
  TouchableOpacity,
  StyleSheet,
  ImageBackground,
  View,
  Image,
  KeyboardAvoidingView,
  StatusBar,
  Button,
} from "react-native";
import { withFirebase } from "../../components/firebase";

import InputEmail from "../../components/login/LoginForm/InputEmail";
import InputPassword from "../../components/login/LoginForm/InputPassword";
import SubmitButton from "../../components/login/LoginForm/SubmitButton";
import LinearGradient from "react-native-linear-gradient";
import Alert from "../../components/common/Alert";

import LogoMarca from "../../components/common/svgs/LogoMarca";
import LoginBackground from "../../components/common/svgs/LoginBackground";

class LoginScreen extends React.Component {
  state = {
    email: "",
    password: "",
    loading: false,
    authenticated: null,
    showAlert: false,
    errorEmail: false,
    errorPassword: false,
    buttonTitle: "Estou ciente",
  };

  authenticate() {
    let validated = this.validations();

    if (validated) {
      this.setState({ loading: true });

      this.props.firebase
        .signInWithEmailAndPassword(this.state.email, this.state.password)
        .then(() => {
          this.props.navigation.navigate("UserArea", { screen: "Dashboard" });
        })
        .catch((error) => {
          console.log(error);
          this.handleErrorCode(error.code);
          this.setState({
            loading: false,
            authenticated: false,
          });
        });
    }
  }

  validations() {
    if (!this.state.email) {
      this.setState({ errorEmail: true });
      return false;
    }

    if (!this.state.password) {
      this.setState({ errorPassword: true });
      return false;
    }

    return true;
  }

  handleErrorCode(errorCode) {
    console.log(errorCode);
    switch (errorCode) {
      case "auth/wrong-password":
        this.setState({
          errorCode: errorCode,
          errorTitle: "Senha inválida",
          errorMessage: "Que pena! A senha que você inseriu é inválida.",
          showAlert: true,
          buttonTitle: "Estou ciente",
        });
        break;

      case "auth/user-not-found":
        this.setState({
          errorCode: errorCode,
          errorTitle: "E-mail não encontrado",
          errorMessage:
            "Que pena! O E-mail que você inseriu não está cadastrado em nossa base de dados. Cadastre-se!",
          showAlert: true,
          buttonTitle: "Cadastrar",
        });
        break;

      case "auth/invalid-email":
        this.setState({
          errorCode: errorCode,
          errorTitle: "E-mail inválido",
          errorMessage:
            "Que pena! O E-mail inserido não está nos padrões aceitos pelo MyFiis. Por favor, escolha outro E-mail e tente novamente.",
          showAlert: true,
          buttonTitle: "Estou ciente",
        });
        break;

      default:
        console.log(errorCode);
        this.setState({
          errorCode: errorCode,
          errorTitle: "Erro",
          errorMessage:
            "Que pena! Ocorreu um erro inesperado ao realizar Login. Contate o nosso suporte.",
          showAlert: true,
          buttonTitle: "Estou ciente",
        });
        break;
    }
  }

  onPasswordChange(e) {
    this.setState({ password: e });
  }

  onEmailChange(e) {
    this.setState({ email: e });
  }

  renderForgotPasswordScreen() {
    this.props.navigation.navigate("ForgotPassword");
  }

  renderContent() {
    const failed = () => {
      if (
        this.state.authenticated === null ||
        this.state.authenticated === true
      ) {
        return false;
      } else {
        return true;
      }
    };

    return (
      <KeyboardAvoidingView behavior="padding">
        <View style={styles.loginForm}>
          <StatusBar
            barStyle="light-content"
            translucent={true}
            backgroundColor="transparent"
          />

          <LoginBackground
            style={{
              zIndex: -1,
              position: "absolute",
              marginTop: 13,
              width: 100,
            }}
          />

          <LogoMarca style={styles.icon} />

          <InputEmail
            value={this.state.email}
            onChange={this.onEmailChange.bind(this)}
            failed={failed() || this.state.errorEmail}
          />

          <InputPassword
            value={this.state.password}
            onChange={this.onPasswordChange.bind(this)}
            failed={failed() || this.state.errorPassword}
          />

          <TouchableOpacity
            style={styles.forgotPassword}
            onPress={this.renderForgotPasswordScreen.bind(this)}
          >
            <Text style={styles.forgotPasswordText}>Esqueceu a senha?</Text>
          </TouchableOpacity>

          <SubmitButton
            onPress={this.authenticate.bind(this)}
            isLoading={this.state.loading}
          />
        </View>
      </KeyboardAvoidingView>
    );
  }

  showAlert() {
    this.setState({ showAlert: true });
  }

  hideAlert() {
    if (this.state.errorCode === "auth/user-not-found") {
      this.props.navigation.navigate("NewUser");
    }
    this.setState({ showAlert: false });
  }

  render() {
    const { showAlert, errorTitle, errorMessage } = this.state;
    return (
      <LinearGradient
        useAngle={true}
        angle={119.21}
        locations={[0, 1]}
        start={{ x: 0.0, y: 0.0 }}
        end={{ x: 1, y: 1 }}
        colors={["#26BFBD", "#00E1B5"]}
        style={styles.mainView}
      >
        {this.renderContent()}

        <TouchableOpacity
          style={styles.signup}
          onPress={() => this.props.navigation.navigate("NewUser")}
        >
          <Text style={styles.signupText}>Novo no MyFiis? Cadastre-se</Text>
        </TouchableOpacity>

        <Alert
          show={showAlert}
          title={errorTitle}
          message={errorMessage}
          onConfirm={this.hideAlert.bind(this)}
          onCancel={this.hideAlert.bind(this)}
          confirmText={this.state.buttonTitle}
        />
      </LinearGradient>
    );
  }
}

const styles = StyleSheet.create({
  mainView: {
    flex: 1,
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#1EBEA5",
  },

  loginForm: {
    height: 380,
    width: 295,
    borderRadius: 0,
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
  },

  signup: {
    position: "absolute",
    bottom: 40,
  },

  signupText: {
    color: "#FFFFFF",
    fontFamily: "Montserrat-Regular",
    fontStyle: "normal",
    fontWeight: "500",
    fontSize: 12,
    lineHeight: 15,
    padding: 4,
  },

  forgotPasswordText: {
    fontFamily: "Montserrat-Regular",
    color: "#909090",
    fontSize: 12,
    fontWeight: "500",
    lineHeight: 12,
    padding: 3,
  },

  forgotPassword: {
    alignSelf: "flex-end",
    marginRight: 10,
    marginTop: 0,
    marginBottom: 10,
    right: 10,
    fontFamily: "Montserrat-Regular",
    color: "#909090",
    fontSize: 10,
    fontWeight: "500",
    fontStyle: "normal",
  },

  failMessage: {
    fontSize: 13,
    color: "red",
    fontWeight: "bold",
    alignSelf: "center",
  },

  viewFailMessage: {
    marginTop: 10,
    justifyContent: "center",
    textAlign: "center",
    maxWidth: 300,
    borderColor: "black",
  },

  icon: {
    paddingBottom: 0,
    marginTop: 40,
    marginBottom: 10,
  },
});

export default withFirebase(LoginScreen);
