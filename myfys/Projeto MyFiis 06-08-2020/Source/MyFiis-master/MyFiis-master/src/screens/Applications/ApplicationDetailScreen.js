import React from "react";
import {
  View,
  StyleSheet,
  KeyboardAvoidingView,
  Text,
  TextInput,
  Platform,
  TouchableWithoutFeedback,
  Keyboard,
} from "react-native";
import DatePicker from "react-native-datepicker";
import { TextInputMask } from "react-native-masked-text";
import SearchableDropdown from "react-native-searchable-dropdown";
import DefaultRoundedButton from "../../components/common/buttons/DefaultRoundedButton";
import Spinner from "../../components/common/Spinner";
import { useNavigation } from "@react-navigation/native";
import ScreenHeader from "../../components/common/ScreenHeader";
import MainHeader from "../../components/common/MainHeader";
import { withFirebase } from "../../components/firebase";
import AwesomeAlert from "react-native-awesome-alerts";
import { normalize } from "../../lib/normalize";

class ApplicationDetailScreen extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      fiiEdited: null,
      date: null,
      value: null,
      quantity: null,
      fii: null,
      loading: false,
      canSubmit: false,
      fiisList: [],
      showConfirmDelete: false,
      fiiComponentSearchKey: 0,
    };
  }

  componentDidMount() {
    let fiis = [];

    for (let i = 0; i < this.props.firebase.database.fiis.length; i++) {
      fiis.push({ name: this.props.firebase.database.fiis[i].code });
    }

    this.setState({ fiisList: fiis });

    this._unsubscribeFocus = this.props.navigation.addListener("focus", () => {
      if (
        this.props.route.params &&
        this.props.route.params.action == "edit" &&
        this.props.route.params.editObj
      ) {
        let obj = this.props.route.params.editObj;

        let day = obj.date.substr(8, 2);
        let month = obj.date.substr(5, 2);
        let year = obj.date.substr(0, 4);

        this.setState({
          fiiEdited: obj.fii,
          fii: obj.fii,
          value: (obj.price / 100).toFixed(2),
          quantity: obj.quantity.toString(),
          date: day + "/" + month + "/" + year,
        });
      }
    });

    this._unsubscribeBlur = this.props.navigation.addListener("blur", () => {
      //Clear
      this.clearState();
    });
  }

  componentWillUnmount() {
    this._unsubscribeFocus();
    this._unsubscribeBlur();
  }

  clearState() {
    this.setState({
      loading: false,
      date: null,
      value: null,
      quantity: null,
      fii: null,
      showConfirmDelete: false,
      canSubmit: false,
      fiiEdited: null,
      fiiComponentSearchKey: 100 + Math.floor((200 - 100) * Math.random()), //Forçar atualizar o componente
    });
  }

  onChangeDate(e) {
    this.setState({ date: e }, () => {
      this.checkCanSubmit();
    });
  }

  onChangeQuantity(e) {
    this.setState({ quantity: e }, () => {
      this.checkCanSubmit();
    });
  }

  onChangeValue(e) {
    this.setState({ value: e }, () => {
      this.checkCanSubmit();
    });
  }

  onChangeFii(e) {
    this.setState({ fii: e }, () => {
      this.checkCanSubmit();
    });
  }

  checkCanSubmit() {
    let value = this.state.value
      ? parseInt(this.state.value.toString().replace(/[^0-9]/g, ""))
      : 0;
    let quantity = this.state.quantity
      ? parseInt(this.state.quantity.toString().replace(/[^0-9]/g, ""))
      : 0;

    if (
      !this.state.canSubmit &&
      value > 0 &&
      this.state.date &&
      this.state.fii &&
      quantity > 0
    ) {
      this.setState({
        canSubmit: true,
      });
    } else if (
      this.state.canSubmit &&
      (value < 1 || !this.state.date || !this.state.fii || quantity < 1)
    ) {
      this.setState({
        canSubmit: false,
      });
    }
  }

  async onSubmit() {
    this.setState({
      loading: true,
    });

    let value = parseInt(this.state.value.toString().replace(/[^0-9]/g, ""));
    let quantity = parseInt(
      this.state.quantity.toString().replace(/[^0-9]/g, "")
    );

    let day = this.state.date.substr(0, 2);
    let month = this.state.date.substr(3, 2);
    let year = this.state.date.substr(6, 4);
    let fiis_code = this.state.fii.toUpperCase();

    try {
      if (this.props.route.params.action == "edit") {
        this.props.firebase.updateApplication({
          id: this.props.route.params.editObj.id,
          data: {
            fii: fiis_code,
            price: value,
            date: year + "-" + month + "-" + day,
            quantity: quantity,
          },
        });
      } else {
        this.props.firebase.addApplication({
          fii: fiis_code,
          price: value,
          date: year + "-" + month + "-" + day,
          quantity: quantity,
        });
      }

      //Se usar await para adicionar ou alterar e o celular estiver offline, o controle não volta mais. Fica esperando o firestore responder.
      await new Promise((resolve) => setTimeout(resolve, 1000)); //Dar um delay para os novos dados entrarem no cache, ja que não estamos esperando a resposta do servidor
    } catch (e) {
      console.logs("Error on manage application", e);
    }

    if (
      this.props.route.params.action == "add" &&
      this.props.route.params.fiiOrigin
    ) {
      if (this.props.route.params.fiiOrigin == fiis_code)
        this.props.navigation.goBack();
      else this.props.navigation.navigate("Wallet");
    } else {
      this.props.navigation.goBack();
    }

    this.clearState();
  }

  async onDelete() {
    try {
      if (this.props.route.params.action == "edit") {
        await this.props.firebase.deleteApplication({
          id: this.props.route.params.editObj.id,
        });
      }
    } catch (e) {
      console.log("Error onDelete application", e);
    }

    this.props.navigation.goBack();
  }

  renderButton() {
    if (this.state.loading) {
      return <Spinner size="large" />;
    }

    return (
      <DefaultRoundedButton
        disabled={!this.state.canSubmit}
        onPress={this.onSubmit.bind(this)}
        text={
          this.props.route.params.action == "edit" ? "ATUALIZAR" : "ADICIONAR"
        }
      />
    );
  }

  render() {
    return (
      <View style={{ backgroundColor: "#FAFAFA", flex: 1 }}>
        <MainHeader navigation={this.props.navigation} />
        <ScreenHeader
          title={
            (this.props.route.params.action == "edit"
              ? "Editar"
              : "Adicionar") + " Aplicação"
          }
          navigation={this.props.navigation}
          deleteFunction={
            this.props.route.params.action == "edit"
              ? function () {
                  this.setState({ showConfirmDelete: true });
                }.bind(this)
              : null
          }
        />

        <KeyboardAvoidingView
          behavior={Platform.OS == "ios" ? "padding" : "heigth"}
          style={{ flex: 1 }}
        >
          <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
            <View style={{ paddingHorizontal: 20, paddingTop: 50, flex: 1 }}>
              <View style={styles.row}>
                <Text style={{ ...styles.inputLabel, ...{ flex: 2 } }}>
                  Nome do Fundo
                </Text>
                <Text style={{ ...styles.inputLabel, ...{ flex: 1 } }}>
                  Preço da Cota
                </Text>
              </View>

              <View style={styles.row}>
                <SearchableDropdown
                  key={"fii-search" + this.state.fiiComponentSearchKey}
                  onItemSelect={(item) => {
                    this.onChangeFii(item.name);
                  }}
                  containerStyle={{
                    flex: 2,
                    marginHorizontal: 5,
                    borderRadius: 30,
                    borderColor: "#29B5A4",
                    borderWidth: 1,
                    fontSize: normalize(12),
                    paddingLeft: 15,
                    backgroundColor: "#FFFFFF",
                    color: "#222222",
                  }}
                  itemStyle={{
                    padding: 10,
                    borderWidth: 0,
                  }}
                  itemTextStyle={{ color: "#222222", borderWidth: 0 }}
                  itemsContainerStyle={{
                    maxHeight: 120,
                    borderWidth: 0,
                  }}
                  items={this.state.fiisList}
                  defaultIndex={0}
                  resetValue={false}
                  textInputProps={{
                    placeholder: this.state.fiiEdited
                      ? this.state.fiiEdited
                      : "Digite o código do Fii",
                    placeholderTextColor: this.state.fiiEdited
                      ? "#222"
                      : "#DADADA",
                    underlineColorAndroid: "transparent",
                    style: {
                      height: 42,
                      fontSize: normalize(12),
                      color: "#222222",
                    },
                    onTextChange: (text) => {
                      this.onChangeFii(text);
                    },
                  }}
                  listProps={{
                    nestedScrollEnabled: true,
                  }}
                />

                <TextInputMask
                  style={{ ...styles.textInput, ...{ flex: 1 } }}
                  onChangeText={this.onChangeValue.bind(this)}
                  placeholder={"Preço da cota"}
                  type={"money"}
                  autoCorrect={false}
                  keyboardType={"number-pad"}
                  options={{
                    precision: 2,
                    separator: ",",
                    delimiter: ".",
                    unit: "R$ ",
                  }}
                  value={this.state.value}
                  placeholderTextColor="#DADADA"
                />
              </View>

              <View style={{ marginTop: 30 }}>
                <View style={styles.row}>
                  <Text style={{ ...styles.inputLabel, ...{ flex: 2 } }}>
                    Data da Operação
                  </Text>
                  <Text style={{ ...styles.inputLabel, ...{ flex: 1 } }}>
                    Qt. Comprada
                  </Text>
                </View>

                <View style={styles.row}>
                  <DatePicker
                    style={{ ...styles.dateInput, ...{ flex: 2 } }}
                    onDateChange={this.onChangeDate.bind(this)}
                    placeholder={"Data da operação"}
                    autoCorrect={false}
                    autoFocus={false}
                    date={this.state.date}
                    mode="date"
                    format="DD/MM/YYYY"
                    minDate="01/01/1993"
                    maxDate="01/01/2110"
                    confirmBtnText="Confirmar"
                    cancelBtnText="Cancelar"
                    showIcon={false}
                    customStyles={{
                      dateInput: {
                        borderWidth: 0,
                      },
                      dateText: {
                        color: "#222222",
                        flex: 1,
                        alignSelf: "flex-start",
                        marginTop: 12,
                        marginLeft: 4,
                        fontSize: normalize(12),
                      },
                      placeholderText: {
                        flex: 1,
                        alignSelf: "flex-start",
                        marginTop: 12,
                        marginLeft: 4,
                        fontSize: normalize(12),
                        color: "#DADADA",
                      },
                    }}
                  />

                  <TextInput
                    style={{ ...styles.textInput, ...{ flex: 1 } }}
                    onChangeText={this.onChangeQuantity.bind(this)}
                    placeholder={"Qt. Comprada"}
                    autoCorrect={false}
                    keyboardType={"number-pad"}
                    value={this.state.quantity}
                    placeholderTextColor="#DADADA"
                  />
                </View>
              </View>

              <View style={styles.addButton}>{this.renderButton()}</View>
            </View>
          </TouchableWithoutFeedback>
        </KeyboardAvoidingView>

        {this.state.showConfirmDelete ? (
          <AwesomeAlert
            show={true}
            showProgress={false}
            title={"Atenção"}
            message={"Confirma a exclusão dessa aplicação?"}
            closeOnTouchOutside={true}
            closeOnHardwareBackPress={false}
            showCancelButton={true}
            showConfirmButton={true}
            cancelText="Cancelar"
            confirmText="Sim"
            confirmButtonColor="#DD6B55"
            onCancelPressed={() => {
              this.setState({ showConfirmDelete: false });
            }}
            onConfirmPressed={() => {
              this.setState(
                { showConfirmDelete: false, loading: true },
                function () {
                  this.onDelete();
                }
              );
            }}
            confirmButtonStyle={{
              backgroundColor: "rgba(58, 176, 162, 0.5)",
            }}
          />
        ) : null}
      </View>
    );
  }
}

const styles = StyleSheet.create({
  inputLabel: {
    marginLeft: 10,
    color: "#222222",
    fontSize: normalize(12),
  },

  row: {
    flexDirection: "row",
    alignSelf: "center",
    justifyContent: "space-between",
  },

  addButton: {
    marginTop: 60,
    justifyContent: "center",
    alignSelf: "center",
    marginLeft: 10,
    marginRight: 10,
    width: "100%",
  },

  textInput: {
    marginHorizontal: 5,
    borderRadius: 30,
    borderColor: "#29B5A4",
    borderWidth: 1,
    height: 45,
    fontSize: normalize(12),
    paddingLeft: 15,
    backgroundColor: "#FFFFFF",
    color: "#222222",
  },

  dateInput: {
    marginHorizontal: 5,
    borderRadius: 30,
    borderColor: "#29B5A4",
    borderWidth: 1,
    height: 45,
    paddingLeft: 15,
    backgroundColor: "#FFFFFF",
  },
});

// Wrap and export
export default withFirebase(function (props) {
  const navigation = useNavigation();

  return <ApplicationDetailScreen {...props} navigation={navigation} />;
});
