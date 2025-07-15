import React from "react";
import {
  ScrollView,
  Text,
  View,
  StyleSheet,
  TextInput,
  KeyboardAvoidingView,
  Keyboard,
  TouchableWithoutFeedback,
  SafeAreaView
} from "react-native";
import { Icon } from "react-native-elements";
import MainHeader from "../../components/common/MainHeader";
import ScreenHeader from "../../components/common/ScreenHeader";
import SmallRoundedButton from "../../components/common/buttons/SmallRoundedButton";
import { withFirebase } from "../../components/firebase";
import AwesomeAlert from "react-native-awesome-alerts";

class ContactScreen extends React.Component {
  state = {
    message: "",
    loading: false,
    showAlert: false,
    canSubmit: false,
  };

  onChangeMessage(e) {
    this.setState(
      {
        message: e,
        canSubmit: false,
      },
      () => {
        if (this.state.message.length) {
          this.setState({
            canSubmit: true,
          });
        }
      }
    );
  }

  async onSubmit() {
    this.setState({
      loading: true,
    });

    if (this.state.message == "") {
      return;
    }

    let data = {
      message: this.state.message,
    };

    let result = null;

    try {
      // console.log(this.props.firebase.getInTouch());
      result = await this.props.firebase.getInTouch(data);
    } catch (e) {
      console.log("Error ", e);
    }

    if (result) {
      this.setState({
        loading: false,
        message: "",
        showAlert: true,
        loading: false,
      });
    }

    this.setState({
      loading: false,
    });
  }

  render() {
    return (
     
      <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
      <View style={{ flex: 1, backgroundColor: "#FAFAFA" }}>
        <MainHeader navigation={this.props.navigation} />
        <ScreenHeader title="Contato" />
       
<ScrollView>
        <View style={styles.container}>

            <View style={styles.contactForm}>
              <View style={styles.headerForm}>
                <Text style={styles.title}>Queremos ouvir você!</Text>
              </View>

              <View style={styles.bodyForm}>
                <Text style={styles.label}>Mensagem:</Text>
                <TextInput
                  multiline={true}
                  numberOfLines={10}
                  onChangeText={() => {}}
                  style={styles.textArea}
                  value={this.state.message}
                  textAlignVertical="top"
                  placeholder="Deixe aqui elogios, reclamações, sugestões..."
                  onChangeText={this.onChangeMessage.bind(this)}
                />

                <SmallRoundedButton
                  text="Enviar"
                  loading={this.state.loading}
                  onPress={this.onSubmit.bind(this)}
                  canSubmit={this.state.canSubmit}
                />
              </View>
            </View>

        </View>
        </ScrollView>

        <AwesomeAlert
          show={this.state.showAlert}
          showProgress={false}
          title="Sucesso"
          message="Contato registrado com sucesso!"
          closeOnTouchOutside={true}
          closeOnHardwareBackPress={false}
          showCancelButton={false}
          showConfirmButton={true}
          confirmText="Ok"
          confirmButtonColor="#DD6B55"
          onCancelPressed={() => {
            this.setState({ showAlert: false });
          }}
          onConfirmPressed={() => {
            this.setState({ showAlert: false });
          }}
          confirmButtonStyle={styles.confirmButtonColor}
        />
      </View>
      
      </TouchableWithoutFeedback>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    marginHorizontal: 10,
    width: "100%",
  },

  confirmButtonColor: {
    backgroundColor: "rgba(58, 176, 162, 0.5)",
  },

  contactForm: {
    alignSelf: "center",
    marginTop: 20,
    backgroundColor: "#FFFF",
    borderRadius: 15,
    padding: 10,
    height: 350,
    width: "100%",
    borderColor: "black",
    borderWidth: 0.3,
    width: 260,
  },

  headerForm: {
    flex: 1,
    height: 30,
    justifyContent: "center",
  },

  bodyForm: {
    flex: 4,
  },

  title: {
    flexDirection: "row",
    alignSelf: "center",
    color: "#868686",
  },

  textInput: {
    height: 37,
    borderRadius: 20,
    borderColor: "#E4E4E4",
    borderWidth: 1,
    paddingLeft: 10,
    marginBottom: 10,
    color: "rgba(58, 176, 162, 1)",
  },

  textArea: {
    height: 190,
    borderRadius: 10,
    borderColor: "#E4E4E4",
    borderWidth: 1,
    paddingLeft: 10,
    marginBottom: 10,
    color: "rgba(58, 176, 162, 1)",
  },

  label: {
    fontWeight: "bold",
    fontSize: 12,
    lineHeight: 15,
    color: "#868686",
    marginLeft: 5,
    marginBottom: 1,
  },
});

export default withFirebase(ContactScreen);
