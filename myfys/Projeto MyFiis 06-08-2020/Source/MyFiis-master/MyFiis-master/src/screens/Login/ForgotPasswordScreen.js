import React from "react";
import { Text, View, StyleSheet, ScrollView } from "react-native";
import RoundedInput from "../../components/common/inputs/RoundedInput";
import ForwardButton from "../../components/common/buttons/ForwardButton";
import Alert from "../../components/common/Alert";
import { withFirebase } from "../../components/firebase";
import MainHeader from "../../components/common/MainHeader";
import ScreenHeader from "../../components/common/ScreenHeader";

class ForgotPasswordScreen extends React.Component {
  static navigationOptions = {
    drawerLabel: "Esqueci senha",
  };

  state = {
    canSubmit: false,
    email: "",
    loading: false,
    errorTitle: "",
    errorMessage: "",
    showAlert: false,
    redirectLogin: false, //redirecionar ou não para a tela de login
    redirectSignup: false,
    confirmText: "Tentar novamente",
    invalidEmail: false,
  };

  onChangeText(e) {
    this.setState(
      {
        email: e,
      },
      () => {
        if (this.state.email.length) {
          this.setState({
            canSubmit: true,
          });
        } else {
          this.setState({
            canSubmit: false,
          });
        }
      }
    );
  }

  onSubmitEmail() {
    let email = this.state.email;

    if (!email) {
      this.setState({
        invalidEmail: true,
      });

      return;
    }

    this.setState({
      loading: true,
      redirectLogin: false,
      redirectSignup: false,
    });

    this.props.firebase
      .passwordReset(email)
      .then(
        function () {
          this.setState({
            errorTitle: "Sucesso",
            errorMessage:
              "Email enviado com sucesso para recuperar a senha. Após confirmar o seu E-mail, faça o Login no MyFiis e tenha um bom uso!",
            showAlert: true,
            loading: false,
            redirectLogin: true,
            confirmText: "Fazer Login",
          });
        }.bind(this)
      )
      .catch(
        function (error) {
          this.handleErrorCode(error.code);
        }.bind(this)
      );
  }

  handleErrorCode(errorCode) {
    switch (errorCode) {
      case "auth/invalid-email":
        this.setState({
          errorCode: errorCode,
          errorTitle: "E-mail inválido",
          errorMessage:
            "Que pena! O E-mail inserido não está nos padrões aceitos pelo MyFii. Por favor, escolha outro E-mail e tente novamente.",
          showAlert: true,
          loading: false,
        });
        break;

      case "auth/user-not-found":
        this.setState({
          errorCode: errorCode,
          errorTitle: "E-mail não encontrado",
          errorMessage:
            "O E-mail que você digitou não existe em nossa plataforma. Cadastre-se, clicando no botão abaixo.",
          showAlert: true,
          loading: false,
          redirectSignup: true,
          confirmText: "Cadastrar",
        });
        break;

      default:
        this.setState({
          errorCode: errorCode,
          errorTitle: "Erro",
          errorMessage:
            "Que pena! Ocorreu um erro inesperado ao cadastrar. Contate o nosso suporte.",
          showAlert: true,
          loading: false,
        });
        break;
    }
  }

  redirectIfNecessary() {
    if (this.state.redirectLogin === true) {
      this.props.navigation.navigate("Login");
    }

    if (this.state.redirectSignup === true) {
      this.props.navigation.navigate("NewUser");
    }
  }

  hideAlert() {
    this.setState({ showAlert: false });
    this.redirectIfNecessary();
  }

  showAlert() {
    this.setState({ showAlert: true });
  }

  onConfirmAlert() {
    this.setState({ showAlert: false });
    this.redirectIfNecessary();
  }

  render() {
    const { showAlert, errorMessage, errorTitle } = this.state;

    return (
      <>
        <MainHeader />

        <ScrollView style={styles.scrollView}>
          <View style={styles.container}>
            <ScreenHeader
              title="Esqueci minha senha"
              navigation={this.props.navigation}
            />

            <Text style={styles.text}>
              Digite o seu endereço de e-mail para redefinição de senha.{" "}
              <Text style={styles.mandatory}>Obrigatório *</Text>
            </Text>

            <RoundedInput
              label="Email"
              type="email"
              placeholder="Insira o seu endereço de email *"
              onChange={this.onChangeText.bind(this)}
              autoCompleteType="email"
              autoCorrect={false}
              keyboardType="email-address"
            />

            <View style={styles.viewButton}>
              <ForwardButton
                enabled={this.state.canSubmit}
                isLoading={this.state.loading}
                onPress={this.onSubmitEmail.bind(this)}
              />
            </View>
          </View>
        </ScrollView>

        <Alert
          show={showAlert}
          title={errorTitle}
          message={errorMessage}
          confirmText={this.state.confirmText}
          onConfirm={this.onConfirmAlert.bind(this)}
          onCancel={this.hideAlert.bind(this)}
        />
      </>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "flex-start",
    marginHorizontal: 25,
    backgroundColor: "#FAFAFA",
  },
  text: {
    color: "rgba(58, 176, 162, 0.5)",
    fontWeight: "bold",
  },
  mandatory: {
    color: "#d3d3d3",
  },
  viewButton: {
    alignSelf: "flex-end",
    marginTop: 10,
    marginRight: 5,
  },
  scrollView: {
    backgroundColor: "#FAFAFA",
  },
});

export default withFirebase(ForgotPasswordScreen);
