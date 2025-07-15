import React from "react";
import { View, StyleSheet, Text, FlatList, Platform } from "react-native";
import { withFirebase } from "../../components/firebase";
import Title from "../../components/dashboard/Title";
import Summary from "../../components/dashboard/Summary";
import FiisListItem from "./FiisListItem";
import Spinner from "../../components/login/LoginForm/Spinner";
import MainHeader from "../../components/common/MainHeader";
import EmptyWallet from "../../components/common/svgs/EmptyWallet";
import Donate from "../../components/dashboard/Donate";
import { CommonActions } from "@react-navigation/native";
import { normalize } from "../../lib/normalize";

class DashboardScreen extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      loggedIn: false,
      loading: true,
      focus: true,
      totalApplied: 0,
      totalProfit: 0,
      totalProfitability: 0,
      userAppications: [],
      userDividends: [],
      consolidatedFiiList: [],
      showDonationBanner: true,
    };

    this.isIos = Platform.OS === "ios";
  }

  async loadResumeData() {
    try {
      if (!this.state.loggedIn) return;

      let consolidatedFiiList = [];
      let consolidatedFiis = {};
      let apps = await this.props.firebase.getApplications();
      let dividends = await this.props.firebase.getDividends();

      let totalApplied = 0;
      let totalProfit = 0;
      let totalProfitability = 0;

      for (let i = 0; i < apps.length; i++) {
        const app = apps[i];

        totalApplied += app.quantity * app.price;

        if (!consolidatedFiis[app.fii]) {
          consolidatedFiis[app.fii] = {
            code: app.fii,
            numStocks: 0,
            totalApplied: 0,
            totalProfit: 0,
            sumPrices: 0,
            numDividendEvents: 0,
            averagePrice: 0,
            profitability: 0,
          };
        }

        consolidatedFiis[app.fii].numStocks += app.quantity;
        consolidatedFiis[app.fii].totalApplied += app.quantity * app.price;
      }

      for (let i = 0; i < dividends.length; i++) {
        const dividend = dividends[i];

        totalProfit += dividend.total;

        if (!consolidatedFiis[dividend.fii]) {
          consolidatedFiis[dividend.fii] = {
            code: dividend.fii,
            numStocks: 0,
            totalApplied: 0,
            totalProfit: 0,
            sumPrices: 0,
            numDividendEvents: 0,
            averagePrice: 0,
            profitability: 0,
          };
        }

        consolidatedFiis[dividend.fii].totalProfit += dividend.total;
        consolidatedFiis[dividend.fii].sumPrices +=
          dividend.total / 100 / dividend.quantity;
        consolidatedFiis[dividend.fii].numDividendEvents += 1;
      }

      for (const key in consolidatedFiis) {
        const fii = consolidatedFiis[key];

        if (fii.numStocks > 0) {
          consolidatedFiis[key].averagePrice =
            fii.totalApplied / 100 / fii.numStocks;

          if (fii.numDividendEvents > 0) {
            consolidatedFiis[key].profitability =
              ((fii.sumPrices / fii.numDividendEvents) * 100) /
              consolidatedFiis[key].averagePrice;

            totalProfitability += consolidatedFiis[key].profitability;
          }
        }

        consolidatedFiiList.push(consolidatedFiis[key]);
      }

      //Sort by profitability
      consolidatedFiiList.sort(function (a, b) {
        return b.profitability - a.profitability;
      });

      totalProfitability =
        totalProfitability / Object.keys(consolidatedFiis).length;

      this.setState({
        totalApplied: totalApplied,
        totalProfit: totalProfit,
        totalProfitability: totalProfitability,
        userAppications: apps,
        userDividends: dividends,
        consolidatedFiiList: consolidatedFiiList,
      });
    } catch (e) {
      console.log("Error on loadResumeData", e);
    }
  }

  componentDidMount() {
    try {
      this._unsubscribeFocus = this.props.navigation.addListener(
        "focus",
        async () => {
          this.setState(
            {
              focus: true,
              loading: true,
            },
            async () => {
              await this.props.firebase.dataSync();
              await this.loadResumeData();
              this.setState({ loading: false });
            }
          );
        }
      );

      this._unsubscribeBlur = this.props.navigation.addListener("blur", () => {
        this.setState({
          focus: false,
        });
      });

      //Monitoramento de status
      //Somente para quando iniciar o app, ja acessar o painel sem ir p tela de login login.
      this.props.firebase.onAuthStateChanged(async (user) => {
        if (user) {
          this.setState({
            loggedIn: true,
          });
        } else {
          this.setState(
            {
              loggedIn: false,
            },
            () => {
              this.props.navigation.dispatch(
                CommonActions.reset({
                  index: 1,
                  routes: [{ name: "Login" }],
                })
              );
              // this.props.navigation.reset("Login");
            }
          );
        }
      });
    } catch (e) {}
  }

  componentWillUnmount() {
    this._unsubscribeFocus();
    this._unsubscribeBlur();
  }

  loadUserName() {
    let name = "";
    if (
      this.props.firebase &&
      this.props.firebase.auth &&
      this.props.firebase.auth.currentUser &&
      this.props.firebase.auth.currentUser.displayName
    ) {
      name = this.props.firebase.auth.currentUser.displayName
        .substr(0, 15)
        .replace(/ .*/, "");
    } else {
      name = "Anônimo";
    }

    return name;
  }

  loadDashboardData() {
    if (this.state.consolidatedFiiList.length == 0) {
      return (
        <EmptyWallet
          style={{ alignSelf: "center", marginTop: 30 }}
          navigation={this.props.navigation}
        />
      );
    }

    return (
      <View style={styles.allData}>
        <View style={styles.summary}>
          <Summary
            totalApplied={this.state.totalApplied}
            totalProfit={this.state.totalProfit}
            totalProfitability={this.state.totalProfitability}
          />
        </View>

        <View style={styles.detail_container}>
          <Text style={styles.detail_title}>Detalhes</Text>

          <FlatList
            showsHorizontalScrollIndicator={false}
            horizontal={false}
            data={this.state.consolidatedFiiList}
            ListEmptyComponent={() => {
              return <View></View>;
            }}
            keyExtractor={(item) => item.code}
            renderItem={({ item }) => {
              return <FiisListItem fii={item} />;
            }}
          />
        </View>
      </View>
    );
  }

  loadDonationBanner() {
    if (!this.isIos) {
      //Mostrar banner em dias impares - Lógica do Dia sim, dia não..
      if (new Date().getDay() % 2 === 0) {
        return null;
      }

      if (!this.state.showDonationBanner) return null;

      return (
        <Donate onClose={() => this.setState({ showDonationBanner: false })} />
      );
    }
  }

  render() {
    //Focus - Para quando cadastrar, so exibir os dados se tiver a página tiver o foco. Poi será direcionado de volta para ca somente após adicionar o nome do usuário no auth.
    if (this.state.loading === true || !this.state.loggedIn) {
      return (
        <View style={styles.containerLoading}>
          <Spinner size="large" />
        </View>
      );
    }

    return (
      <>
        <MainHeader navigation={this.props.navigation} />

        <View style={styles.container}>
          <Title name={this.state.focus ? this.loadUserName() : ""} />

          {this.loadDonationBanner()}
          {this.loadDashboardData()}
        </View>
      </>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#e5e5e540",
    paddingHorizontal: "5%",
  },

  containerLoading: {
    flex: 2,
    alignItems: "center",
    justifyContent: "center",
  },

  allData: {
    flex: 1,
  },

  summary: {
    flex: 1,
    marginTop: "4%",
  },

  detail_container: {
    flex: 3,
    flexDirection: "column",
    justifyContent: "flex-start",
    alignItems: "stretch",
    paddingTop: "4%",
  },

  detail_title: {
    color: "#6C738A",
    fontFamily: "Montserrat-Regular",
    lineHeight: normalize(12),
    fontSize: normalize(10),
  },
});

export default withFirebase(DashboardScreen);
