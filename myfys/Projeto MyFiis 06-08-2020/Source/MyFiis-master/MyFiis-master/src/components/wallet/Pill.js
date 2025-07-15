import React, { Component } from "react";
import {
  View,
  StyleSheet,
  Text,
  ScrollView,
  TouchableOpacity,
  ImageBackground,
} from "react-native";
import { normalize } from "../../lib/normalize";

export default class Pill extends Component {
  constructor(props) {
    super(props);
  }

  onSelectFii() {
    this.props.onSelectFii(this.props.fii);
  }

  render() {
    {
      if (this.props.selected === true) {
        return (
          <TouchableOpacity>
            <ImageBackground
              source={require("../../../assets/wallet/cardbackground.png")}
              style={styles.selectedCard}
            >
              <Text style={styles.selectedCardText}>{this.props.fii.code}</Text>
            </ImageBackground>
          </TouchableOpacity>
        );
      }

      return (
        <TouchableOpacity
          onPress={this.onSelectFii.bind(this)}
          style={styles.unselectedCard}
        >
          <Text style={styles.unselectedCardText}>{this.props.fii.code}</Text>
        </TouchableOpacity>
      );
    }
  }
}

const styles = StyleSheet.create({
  selectedCard: {
    borderColor: "#26BFBD",
    width: 108,
    borderRadius: 8,
    marginLeft: 10,
    height: 34,
    justifyContent: "center",
    elevation: 4,
  },

  selectedCardText: {
    alignSelf: "center",
    paddingTop: 6,
    paddingBottom: 6,
    paddingLeft: 4,
    paddingRight: 4,
    color: "#FFFFFF",
    fontFamily: "Montserrat-Semibold",
    fontSize: normalize(12),
  },

  unselectedCard: {
    borderWidth: 1,
    borderColor: "#EFEFEF",
    width: 108,
    borderRadius: 8,
    marginLeft: 10,
    height: 34,
    justifyContent: "center",
    backgroundColor: "#FFFF",
  },

  unselectedCardText: {
    alignSelf: "center",
    paddingTop: 6,
    paddingBottom: 6,
    paddingLeft: 4,
    paddingRight: 4,
    fontWeight: "500",
    fontSize: normalize(12),
  },
});
