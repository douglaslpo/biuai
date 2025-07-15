import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { normalize } from "../../lib/normalize";
class Title extends React.Component {
  render() {
    let name = this.props.name;
    let nameStr = name.split(" ");
    if (nameStr.length > 2) {
      name = nameStr[0] + " " + nameStr[1];
    }

    if (name.length > 20) {
      name = name.substr(0, 19) + ".";
    }

    return (
      <View style={styles.container}>
        <Text style={styles.name}>Olá{name ? ", " + name : ""}</Text>
        <Text style={styles.greeting}>Seja bem vindo.</Text>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    marginTop: "3%",
  },

  name: {
    fontSize: normalize(30),
    color: "#343F53",
    fontFamily: "Montserrat-Bold",
  },

  greeting: {
    fontSize: normalize(15),
    fontFamily: "Montserrat-Regular",
    lineHeight: normalize(15),
    color: "#343F53",
    fontWeight: "300",
    marginBottom: 0,
  },
});
export default Title;
