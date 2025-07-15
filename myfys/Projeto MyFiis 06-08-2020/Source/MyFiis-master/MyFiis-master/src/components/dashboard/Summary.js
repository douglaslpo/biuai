import React from "react";
import { View, Text, StyleSheet, Image } from "react-native";
import SpeedMeter from "../common/svgs/SpeedMeter";
import BankBuilding from "../common/svgs/BankBuilding";
import Statistics from "../common/svgs/Statistics";
import formatMoney from "../../lib/formatMoney";
import {normalize} from '../../lib/normalize'
class Summary extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    let fontSizeTotal = 15;
    let fontSizeProfit = 15;

    let totalApplied = formatMoney(this.props.totalApplied / 100);

    let totalProfit = formatMoney(this.props.totalProfit / 100);

    let totalProfitability =
      this.props.totalProfitability.toFixed(2).toString().replace(".", ",") +
      "%";

    if (totalApplied.length >= 8 && totalApplied.length < 10) {
      fontSizeTotal = 13;
    } else if (totalApplied.length >= 10) {
      fontSizeTotal = 10;
    }

    if (totalProfit.length >= 8 && totalProfit.length < 10) {
      fontSizeProfit = 13;
    } else if (totalProfit.length >= 10) {
      fontSizeProfit = 10;
    }

    let totalStyle = { ...styles.monetary, fontSize: normalize(fontSizeTotal) };
    let profitStyle = { ...styles.monetary, fontSize: normalize(fontSizeProfit) };

    return (
      <View style={styles.container}>
        <Text style={styles.title}>Resumo da carteira</Text>

        <View style={styles.cards}>
          <View style={styles.cardView}>
            <View style={styles.cardImage}>
              <BankBuilding style={styles.image} />
            </View>
            <View style={styles.cardBottom}>
              <Text style={totalStyle}>
                R$ {""} {totalApplied}
              </Text>
              <Text style={styles.description}>Total aplicado</Text>
            </View>
          </View>

          <View style={styles.cardView}>
            <View style={styles.cardImage}>
              <SpeedMeter style={styles.image} />
            </View>
            <View style={styles.cardBottom}>
              <Text style={profitStyle}>
                R$ {""} {totalProfit}
              </Text>
              <Text style={styles.description}>Rendimento</Text>
            </View>
          </View>

          <View style={styles.cardView}>
            <View style={styles.cardImage}>
              <Statistics style={styles.image} />
            </View>
            <View style={styles.cardBottom}>
              <Text style={styles.monetary2}>{totalProfitability}</Text>
              <Text style={styles.description}>Rentabilidade</Text>
            </View>
          </View>
        </View>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },

  title: {
    flex: 1,
    color: "#6C738A",
    lineHeight: normalize(12),
    fontSize: normalize(10),
    fontFamily: "Montserrat-Regular",
  },

  cards: {
    flex: 4,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },

  cardView: {
    justifyContent: "center",
    alignItems: "center",
    borderRadius: 10,
    borderColor: "black",
    backgroundColor: "#FFFF",
    height: "100%",
    width: "30%",
    shadowColor: "rgba(0, 0, 0, 0.25)",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.8,
    shadowRadius: 2,
    elevation: 1,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 3,
    },
    shadowOpacity: 0.29,
    shadowRadius: 4.65,
    elevation: 7,
  },

  monetary: {
    fontFamily: "Montserrat-Medium",
    fontSize: normalize(15),
    lineHeight: normalize(18),
    color: "#0AC786",
    alignSelf: "center",
    fontStyle: "normal",
  },

  monetary2: {
    fontFamily: "Montserrat-Medium",
    fontSize: normalize(15),
    lineHeight: normalize(18),
    color: "#FF9F00",
    alignSelf: "center",
    fontStyle: "normal",
  },

  description: {
    color: "#6C738A",
    fontFamily: "Montserrat-SemiBold",
    fontSize: normalize(10),
    lineHeight: normalize(12),
    alignSelf: "center",
  },

  image: {
    flex: 1,
  },

  cardImage: {
    flex: 1,
    justifyContent: "center",
  },

  cardBottom: {
    flex: 1,
    alignItems: "center",
    justifyContent: "space-around",
  },
});

export default Summary;
