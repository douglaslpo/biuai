import React, { Component } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StatusBar,
  StyleSheet,
  Platform,
} from "react-native";
import LinearGradient from "react-native-linear-gradient";
import SandwichIcon from "../common/svgs/SandwichIcon";
import { normalize } from "../../lib/normalize";

const headerHeight = Platform.OS === "ios" ? 20 : StatusBar.currentHeight;

class MainHeader extends Component {
  render() {
    return (
      <View style={styles.main}>
        <StatusBar
          barStyle="light-content"
          translucent={true}
          backgroundColor="transparent"
        />

        <LinearGradient
          useAngle={true}
          angle={168.25}
          locations={[0.0, 1.0]}
          colors={["#26BFBD", "#00E1B5"]}
          style={styles.headerBar}
        >
          <View style={styles.headerBarContent}>
            <Text style={styles.my}>My</Text>
            <Text style={styles.fiis}>Fiis</Text>
          </View>

          {this.props.navigation ? (
            <TouchableOpacity
              style={styles.drawer}
              onPress={() => this.props.navigation.openDrawer()}
            >
              <View style={styles.menuIcon}>
                <SandwichIcon style={styles.menuIcon} />
              </View>
            </TouchableOpacity>
          ) : null}
        </LinearGradient>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  main: {
    flexDirection: "column",
  },

  headerBar: {
    height: 60 + headerHeight,
    marginBottom: 0,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "flex-start",
    backgroundColor: "#1EBEA5",
  },

  headerBarContent: {
    paddingTop: headerHeight,
    flexGrow: 1,
    flexDirection: "row",
    justifyContent: "center",
  },

  my: {
    color: "white",
    fontSize: normalize(23),
    fontFamily: "Montserrat-Regular",
  },

  fiis: {
    color: "white",
    fontSize: normalize(23),
    fontFamily: "Montserrat-Bold",
  },

  menuIcon: {
    width: normalize(25),
    height: normalize(25),
    marginLeft: 5,
    color: "white",
  },

  drawer: {
    marginLeft: 10,
    position: "absolute",
    paddingTop: headerHeight,
  },
});

export default MainHeader;
