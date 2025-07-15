import React, { Component } from "react";
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  FlatList,
  TouchableOpacity,
  KeyboardAvoidingView,
  TouchableWithoutFeedback,
  Keyboard,
  Dimensions,
} from "react-native";
import Total from "../../components/common/Total";
import ActionButton from "../../components/common/buttons/ActionButton";
import ScreenHeader from "../../components/common/ScreenHeader";
import MainHeader from "../../components/common/MainHeader";
import DatePicker from "react-native-datepicker";
import Spinner from "../../components/login/LoginForm/Spinner";
import DividendsListItem from "./DividendsListItem";
import { withFirebase } from "../../components/firebase";
import { normalize } from "../../lib/normalize";

const windowHeight = Dimensions.get("window").height;

class DividendsScreen extends Component {
  constructor(props) {
    super(props);

    this.state = {
      dividends: [],
      loading: true,
      averageProfit: 0,
      filterDateStart: null,
      filterDateEnd: null,
      filterFiiCode: null,
      appliedFilter: {},
    };
  }

  async getAveragePrice(filter) {
    try {
      let apps = await this.props.firebase.getApplications(filter);

      let sumValue = 0;
      let quantity = 0;

      for (let i = 0; i < apps.length; i++) {
        quantity += apps[i].quantity;
        sumValue += apps[i].price * apps[i].quantity;
      }

      return quantity > 0 ? sumValue / 100 / quantity : 0;
    } catch (e) {
      console.log(e);
    }

    return 0;
  }

  async loadDividends() {
    try {
      if (
        this.state.appliedFilter.hasOwnProperty("fiiCode") &&
        (this.state.appliedFilter.fiiCode == null ||
          this.state.appliedFilter.fiiCode.trim() == "")
      )
        return;

      let dividends = await this.props.firebase.getDividends(
        this.state.appliedFilter
      );

      let averagePrice = await this.getAveragePrice(this.state.appliedFilter);

      let sumProfit = 0;
      let averageProfit = 0;
      for (let i = 0; i < dividends.length; i++) {
        sumProfit += dividends[i].total / 100 / dividends[i].quantity;
      }

      if (averagePrice > 0 && sumProfit > 0) {
        averageProfit = ((sumProfit / dividends.length) * 100) / averagePrice;
      }

      this.setState({ dividends: dividends, averageProfit: averageProfit });
    } catch (e) {
      console.log("Error on loadDividends", e.message);
    }
  }

  componentDidMount() {
    const execLoadDivid = async function () {
      try {
        await this.loadDividends();
      } catch (e) {
        console.log("Error on execLoadDivid", e);
      }
      this.setState({ loading: false });
    };

    this.unsubscribeFocusListener = this.props.navigation.addListener(
      "focus",
      () => {
        this.setState(
          {
            filterFiiCode: this.props.route.params.fiiScope,
            appliedFilter: { fiiCode: this.props.route.params.fiiScope },
          },
          execLoadDivid
        );
      }
    );

    this.unsubscribeBlurListener = this.props.navigation.addListener(
      "blur",
      () => {
        this.setState({
          loading: true,
          filterFiiCode: null,
          filterDateStart: null,
          filterDateEnd: null,
        });
      }
    );
  }

  componentWillUnmount() {
    this.unsubscribeFocusListener();
    this.unsubscribeBlurListener();
  }

  goToEditPage(application) {
    this.props.navigation.navigate("DividendDetail", {
      action: "edit",
      editObj: application,
    });
  }

  filterPeriod() {
    const exec = async function () {
      try {
        await this.loadDividends();
      } catch (e) {
        console.log("Error on loadDividends", e);
      }
      this.setState({ loading: false });
    };

    if (this.state.filterDateStart && this.state.filterDateEnd) {
      let dayStart = this.state.filterDateStart.substr(0, 2);
      let monthStart = this.state.filterDateStart.substr(3, 2);
      let yearStart = this.state.filterDateStart.substr(6, 4);

      let dayEnd = this.state.filterDateEnd.substr(0, 2);
      let monthEnd = this.state.filterDateEnd.substr(3, 2);
      let yearEnd = this.state.filterDateEnd.substr(6, 4);

      this.setState(
        {
          loading: true,
          appliedFilter: {
            fiiCode: this.state.filterFiiCode,
            period: {
              start: yearStart + "-" + monthStart + "-" + dayStart,
              end: yearEnd + "-" + monthEnd + "-" + dayEnd,
            },
          },
        },
        exec
      );
    }
  }

  filterFiisByCode() {
    const exec = async function () {
      try {
        await this.loadDividends();
      } catch (e) {
        console.log("Error on filterFiisByCode", e);
      }
      this.setState({ loading: false });
    };

    let fii = this.state.filterFiiCode
      ? this.state.filterFiiCode.toUpperCase()
      : null;
    this.setState(
      {
        loading: true,
        appliedFilter: { fiiCode: fii },
        filterDateStart: null,
        filterDateEnd: null,
      },
      exec
    );
  }

  renderList() {
    if (!this.state.loading && this.state.dividends.length > 0) {
      return (
        <FlatList
          showsHorizontalScrollIndicator={false}
          horizontal={false}
          data={this.state.dividends}
          ListEmptyComponent={() => {
            return <View></View>;
          }}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => {
            return (
              <TouchableOpacity onPress={() => this.goToEditPage(item)}>
                <DividendsListItem dividend={item} />
              </TouchableOpacity>
            );
          }}
        />
      );
    }

    return (
      <Text style={{ fontSize: normalize(9), paddingTop: normalize(10) }}>
        Não foram encontrados registros com este filtro.
      </Text>
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
      <View style={{ backgroundColor: "#FAFAFA", flex: 1 }}>
        <MainHeader
          navigation={this.props.navigation}
          style={{ height: windowHeight * 0.05 }}
        />
        <ScreenHeader
          title="Dividendos Recebidos"
          navigation={this.props.navigation}
          style={{ height: windowHeight * 0.08 }}
        />

        <KeyboardAvoidingView
          behavior={Platform.OS == "ios" ? "padding" : "heigth"}
          style={{ flex: 1 }}
        >
          <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
            <View style={styles.container}>
              <Text
                style={{
                  fontFamily: "Montserrat-Medium",
                  fontSize: normalize(11),
                  color: "#343F53",
                  height: windowHeight * 0.03,
                }}
              >
                Período
              </Text>
              <View
                style={{
                  height: windowHeight * 0.05,
                  flexDirection: "row",
                  alignItems: "center",
                }}
              >
                <DatePicker
                  mode="date"
                  placeholder={"Data inicial"}
                  format="DD/MM/YYYY"
                  minDate="01/01/1993"
                  maxDate={
                    this.state.filterDateEnd
                      ? this.state.filterDateEnd
                      : "01/01/2110"
                  }
                  confirmBtnText="Confirmar"
                  cancelBtnText="Cancelar"
                  showIcon={false}
                  date={this.state.filterDateStart}
                  onDateChange={(e) => {
                    this.setState({ filterDateStart: e });
                  }}
                  customStyles={{
                    dateInput: {
                      backgroundColor: "#1EBEA5",
                      borderRadius: 13.5,
                      borderWidth: 1,
                      borderColor: "#00E1B5",
                      maxWidth: 72,
                      height: 27,
                      padding: 6,
                    },
                    dateText: {
                      color: "#FFFF",
                      fontSize: normalize(10),
                      fontWeight: "bold",
                    },
                    placeholderText: {
                      fontSize: normalize(9),
                      color: "#DADADA",
                    },
                  }}
                  style={{
                    alignItems: "flex-start",
                    maxWidth: 75,
                    marginRight: 4,
                  }}
                />

                <Text
                  style={{
                    color: "#222222",
                    fontSize: normalize(13),
                    fontFamily: "Montserrat-Medium",
                  }}
                >
                  à
                </Text>

                <DatePicker
                  mode="date"
                  placeholder={"Data Final"}
                  format="DD/MM/YYYY"
                  minDate={
                    this.state.filterDateStart
                      ? this.state.filterDateStart
                      : "01/01/1993"
                  }
                  maxDate="01/01/2110"
                  confirmBtnText="Confirmar"
                  cancelBtnText="Cancelar"
                  showIcon={false}
                  date={this.state.filterDateEnd}
                  onDateChange={(e) => {
                    this.setState({ filterDateEnd: e });
                  }}
                  customStyles={{
                    dateInput: {
                      backgroundColor: "#1EBEA5",
                      borderRadius: 13.5,
                      borderWidth: 1,
                      borderColor: "#00E1B5",
                      maxWidth: 72,
                      height: 27,
                      padding: 6,
                    },
                    dateText: {
                      color: "#FFFF",
                      fontSize: normalize(10),
                      fontWeight: "bold",
                    },
                    placeholderText: {
                      fontSize: normalize(9),
                      color: "#DADADA",
                    },
                  }}
                  style={{
                    alignItems: "flex-start",
                    maxWidth: 75,
                    marginLeft: 6,
                  }}
                />

                <TouchableOpacity
                  style={{ marginLeft: 5 }}
                  onPress={() => this.filterPeriod()}
                >
                  <Text style={{ fontSize: normalize(12) }}>Filtrar</Text>
                </TouchableOpacity>
              </View>

              <View
                style={{
                  height:
                    windowHeight > 700
                      ? windowHeight * 0.6
                      : windowHeight * 0.56,
                  alignItems: "flex-start",
                }}
              >
                <View
                  style={{
                    flexDirection: "row",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <View style={{ flex: 1 }}>
                    <Text style={{ color: "#343F53", fontSize: normalize(9) }}>
                      {" "}
                      Histórico de Dividendos{" "}
                    </Text>
                  </View>

                  <View style={styles.searchView}>
                    <TextInput
                      style={styles.searchTextInput}
                      placeholderTextColor="#DADADA"
                      placeholder="Pesquisar fundo"
                      onSubmitEditing={(text) => this.filterFiisByCode()}
                      onChangeText={(text) => {
                        this.setState({ filterFiiCode: text });
                      }}
                    />
                  </View>
                </View>

                <View style={styles.appList}>
                  <Text style={styles.title}>Detalhes</Text>

                  {this.renderList()}
                </View>
              </View>

              <View style={{ height: windowHeight * 0.1 }}>
                <Total
                  customStyle={{ color: "#FFCC00" }}
                  caption="Rentabilidade Média"
                  text={
                    this.state.averageProfit
                      .toFixed(2)
                      .toString()
                      .replace(".", ",") + "%"
                  }
                />
                <ActionButton
                  directAccess={{
                    route: "DividendDetail",
                    action: "add",
                    extraData: { fiiOrigin: this.state.filterFiiCode },
                  }}
                />
              </View>
            </View>
          </TouchableWithoutFeedback>
        </KeyboardAvoidingView>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 14,
  },

  searchView: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "flex-end",
    maxHeight: 30,
    maxWidth: 130,
  },
  searchTextInput: {
    flex: 1,
    paddingLeft: 15,
    paddingVertical: 2,
    borderRadius: 15,
    color: "rgba(58, 176, 162, 0.5)",
    fontWeight: "bold",
    borderWidth: 1,
    borderColor: "#29B5A4",
    fontSize: normalize(11),
  },

  appList: {
    flex: 1,
    minWidth: "100%",
    height: 300,
    maxHeight: 300,
    flexDirection: "column",
    justifyContent: "flex-start",
    alignItems: "stretch",
    marginTop: 10,
  },
});

export default withFirebase(DividendsScreen);
