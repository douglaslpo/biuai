import React from "react";
import { View, StyleSheet, Text } from "react-native";
import formatMoney from "../../lib/formatMoney";
import { normalize } from "../../lib/normalize";

const months = [
  "Jan",
  "Fev",
  "Mar",
  "Abr",
  "Mai",
  "Jun",
  "Jul",
  "Ago",
  "Set",
  "Out",
  "Nov",
  "Dez",
];

const DividendsListItem = ({ dividend }) => {
  return (
    <View style={styles.detailBox}>
      <View style={styles.detailBlock}>
        <Text style={styles.titleBlock} opacity={0.5}>
          Fundo
        </Text>
        <Text style={{ ...styles.valueBlock, color: "#0567D0" }}>
          {dividend.fii}
        </Text>
      </View>

      <View style={styles.detailBlock}>
        <Text style={styles.titleBlock} opacity={0.5}>
          Cotas
        </Text>
        <Text style={{ ...styles.valueBlock, color: "#0567D0" }}>
          {dividend.quantity}
        </Text>
      </View>

      <View style={styles.detailBlock}>
        <Text style={styles.titleBlock} opacity={0.5}>
          Rendimento
        </Text>
        <Text style={{ ...styles.valueBlock, color: "#0567D0" }}>
          R$ {formatMoney((dividend.total / 100), true)}
        </Text>
      </View>

      <View style={styles.detailBlock}>
        <Text style={styles.titleBlock} opacity={0.5}>
          Rend Cota
        </Text>
        <Text style={{ ...styles.valueBlock, color: "#05B169" }}>
          R$ {formatMoney((dividend.total / 100 / dividend.quantity), true)}
        </Text>
      </View>

      <View style={styles.detailBlock}>
        <Text style={styles.titleBlock} opacity={0.5}>
          Mês/Ano
        </Text>
        <Text style={{ ...styles.valueBlock, color: "#FF9F00" }}>
          {months[new Date(dividend.date).getMonth()] +
            "/" +
            new Date(dividend.date).getFullYear()}
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
    justifyContent: "space-between",

    marginBottom: 5,
    borderWidth: 2,
    borderColor: "#DADADA",
    borderRadius: 10,
    height: 64,
    padding: 5,
    backgroundColor: "#FFFFFF",
  },

  detailBlock: {
    flex: 1,
    height: "100%",
    alignItems: "center",
    justifyContent: "space-around",
  },

  titleBlock: {
    marginTop: 4,
    color: "rgba(34, 34, 34, 0.5)",
    fontWeight: "bold",
    lineHeight: normalize(10),
    fontSize: normalize(10),
  },

  valueBlock: {
    fontSize: normalize(10),
    lineHeight: normalize(13),
  },
});

export default DividendsListItem;
