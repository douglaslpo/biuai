import React, { Component } from "react";
import { View, Text, TouchableOpacity, Linking } from "react-native";
import LinearGradient from "react-native-linear-gradient";
import Icon from "react-native-vector-icons/AntDesign";

export default class Donate extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    return (
      <TouchableOpacity
        onPress={() =>
          Linking.openURL(
            "https://www.kickante.com.br/campanhas/aplicativo-fundos-imobiliarios"
          )
        }
      >
        <View style={{ height: 141 }}>
          <LinearGradient
            useAngle={true}
            angle={155.54}
            locations={[0, 1]}
            colors={["#26BFBD", "#00E1B5"]}
            style={{ borderRadius: 8, flex: 1, flexDirection: "column" }}
          >
            <View style={{ paddingTop: 3, paddingHorizontal: 3 }}>
              <TouchableOpacity onPress={this.props.onClose}>
                <Icon
                  name="closesquare"
                  style={{
                    fontSize: 20,
                    color: "white",
                    alignSelf: "flex-end",
                  }}
                />
              </TouchableOpacity>
            </View>
            <Text
              style={{
                paddingHorizontal: 15,
                color: "white",
                fontSize: 18,
                fontFamily: "Montserrat-Bold",
              }}
            >
              Colabore conosco!
            </Text>
            <Text
              style={{
                paddingHorizontal: 15,
                color: "white",
                fontSize: 12,
                fontFamily: "Montserrat-Regular",
              }}
            >
              Aprimore a gestão de seus fundos imobiliários contribuindo para a
              evolução do app.
            </Text>
            <TouchableOpacity
              style={{
                marginHorizontal: 15,
                marginTop: 10,
                marginBottom: 10,
                width: "60%",
                flex: 1,
                flexDirection: "row",
                paddingVertical: 8,
                borderRadius: 8,
                backgroundColor: "rgba(255, 255, 255, 0.2)",
              }}
              onPress={() =>
                Linking.openURL(
                  "https://www.kickante.com.br/campanhas/aplicativo-fundos-imobiliarios"
                )
              }
            >
              <View
                style={{
                  flex: 1,
                  flexDirection: "row",
                  justifyContent: "center",
                  alignItems: "center",
                }}
              >
                <Text
                  style={{
                    alignSelf: "center",
                    color: "white",
                    fontSize: 14,
                    fontFamily: "Montserrat-Bold",
                    textAlign: "center",
                  }}
                >
                  QUERO CONTRIBUIR
                </Text>
              </View>
            </TouchableOpacity>
          </LinearGradient>
        </View>
      </TouchableOpacity>
    );
  }
}
