import React from "react";
import {
  View,
  StyleSheet,
  Text,
  Dimensions,
  Platform,
  PixelRatio,
} from "react-native";
import formatMoney from "../../lib/formatMoney";
import { normalize } from "../../lib/normalize";

const FiisListItem = (props) => {
  return (
    <View style={styles.detailBox}>
      <View style={styles.detailBlock}>
        <Text style={styles.titleBlock} opacity={0.5}>
          Fundo
        </Text>
        <Text style={{ ...styles.valueBlock, color: "#0567D0" }}>
          {props.fii.code}
        </Text>
      </View>

      <View style={styles.detailBlock}>
        <Text style={styles.titleBlock} opacity={0.5}>
          Cotas
        </Text>
        <Text style={{ ...styles.valueBlock, color: "#0567D0" }}>
          {props.fii.numStocks}
        </Text>
      </View>

      <View style={styles.detailBlock}>
        <Text style={styles.titleBlock} opacity={0.5}>
          Aplicado
        </Text>
        <Text style={{ ...styles.valueBlock, color: "#05B169" }}>
          R$ {formatMoney(props.fii.totalApplied / 100)}
        </Text>
      </View>

      <View style={styles.detailBlock}>
        <Text style={styles.titleBlock} opacity={0.5}>
          Recebido
        </Text>
        <Text style={{ ...styles.valueBlock, color: "#05B169" }}>
          R$ {formatMoney(props.fii.totalProfit / 100)}
        </Text>
      </View>

      <View style={styles.detailBlock}>
        <Text style={styles.titleBlock} opacity={0.5}>
          Rentabilidade
        </Text>
        <Text style={{ ...styles.valueBlock, color: "#FF9F00" }}>
          {props.fii.profitability.toFixed(2).toString().replace(".", ",") +
            "%"}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  detailBox: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
    marginBottom: 5,
    borderWidth: 2,
    borderColor: "#DADADA",
    borderRadius: 10,
    height: 64,
    padding: 5,
    backgroundColor: "#FFFFFF",
  },

  detailBlock: {
    marginLeft: 5,
    height: "100%",
    alignItems: "center",
    justifyContent: "space-around",
  },

  titleBlock: {
    marginTop: 4,
    color: "rgba(34, 34, 34, 0.5)",
    fontWeight: "bold",
    lineHeight: 13,
    fontSize: normalize(11),
  },

  valueBlock: {
    fontSize: normalize(10),
    lineHeight: 13,
  },
});

export default FiisListItem;
