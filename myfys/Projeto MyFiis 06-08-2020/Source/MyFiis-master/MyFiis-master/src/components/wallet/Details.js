import React from "react";
import { View, StyleSheet, Text, ScrollView } from "react-native";
import formatMoney from "../../lib/formatMoney";
import { normalize } from "../../lib/normalize";

class Details extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  normalizeFont(totalApplied) {
    let fontSize = 13;

    if (totalApplied.length >= 8 && totalApplied.length < 10) {
      fontSize = 12;
    } else if (totalApplied.length >= 10) {
      fontSize = 11;
    }

    let style = {
      ...styles.fontValue,
      fontSize: normalize(fontSize),
    };

    return style;
  }

  render() {
    return (
      <View style={styles.container}>
        <View style={styles.detailBox}>
          {/* Cotas */}
          <View style={styles.detailBlock}>
            <View style={styles.titleBlock}>
              <Text style={styles.fontTitle}>Cotas</Text>
            </View>
            <View style={styles.valueBlock}>
              <View style={styles.valueBlockCotas}>
                <Text style={styles.fontValueCotas}>
                  {this.props.data.quantity}
                </Text>
              </View>
            </View>
          </View>

          {/* Tl. Aplicado */}
          <View style={styles.detailBlock}>
            <View style={styles.titleBlock}>
              <Text style={styles.fontTitle}>Aplicado</Text>
            </View>
            <View style={styles.valueBlock}>
              <Text
                style={this.normalizeFont(
                  formatMoney(this.props.data.totalApplied / 100)
                )}
              >
                R$ {formatMoney(this.props.data.totalApplied / 100)}
                {/* R$ 330.000,00 */}
              </Text>
            </View>
          </View>

          {/* Tl. Recebido */}
          <View style={styles.detailBlock}>
            <View style={styles.titleBlock}>
              <Text style={styles.fontTitle}>Recebido</Text>
            </View>
            <View style={styles.valueBlock}>
              <Text
                style={this.normalizeFont(
                  formatMoney(this.props.data.totalReceived / 100)
                )}
              >
                R$ {formatMoney(this.props.data.totalReceived / 100)}
                {/* R$ 330.000,00 */}
              </Text>
            </View>
          </View>

          {/* Rentabilidade */}
          <View style={styles.detailBlock}>
            <View style={styles.titleBlock}>
              <Text style={styles.fontTitle}>Rentabilidade</Text>
            </View>
            <View style={styles.valueBlock}>
              <Text style={styles.fontValue}>
                {this.props.data.profitability
                  .toFixed(2)
                  .toString()
                  .replace(".", ",") + "%"}
              </Text>
            </View>
          </View>
        </View>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 2,
    flexDirection: "column",
    justifyContent: "space-between",
    alignItems: "stretch",
    paddingHorizontal: 15,
  },

  title: {
    color: "#6C738A",
    lineHeight: normalize(12),
    fontSize: normalize(10),
    marginBottom: 5,
  },

  scrollArea: {
    paddingHorizontal: 0,
  },

  detailBox: {
    flex: 1,
    paddingVertical: normalize(15),
    flexDirection: "row",
    elevation: 4,
    alignItems: "center",
    justifyContent: "space-around",
    marginBottom: 10,
    borderRadius: 10,
    backgroundColor: "#FFFFFF",
    minHeight: normalize(110),
    maxHeight: normalize(120),
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.23,
    shadowRadius: 2.62,
  },

  detailBlock: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },

  titleBlock: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },

  fontTitle: {
    color: "rgba(34, 34, 34, 0.5)",
    fontWeight: "bold",
    lineHeight: normalize(12),
    fontSize: normalize(11),
  },

  valueBlock: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },

  valueBlockCotas: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#0567d01a",
    borderRadius: 4,
    width: normalize(45),
    maxHeight: normalize(20),
  },

  fontValue: {
    fontSize: normalize(13),
    lineHeight: normalize(13),
    color: "#05B169",
  },

  fontValueCotas: {
    color: "#0567D0",
    fontSize: normalize(13),
    lineHeight: normalize(13),
  },
});

export default Details;
