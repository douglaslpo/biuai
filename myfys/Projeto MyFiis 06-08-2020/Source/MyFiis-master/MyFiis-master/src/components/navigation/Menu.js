import React, { useState, Component } from "react";
import { View, Text, StyleSheet, Platform } from "react-native";
import { DrawerContentScrollView, DrawerItem } from "@react-navigation/drawer";
import { FirebaseContext } from "../../../src/components/firebase";
import Icon from "react-native-vector-icons/Ionicons";
import EntypoIcon from "react-native-vector-icons/Entypo";
import { normalize } from "../../lib/normalize";

const isIos = Platform.OS === "ios";

export default class Menu extends Component {
  constructor(props) {
    super(props);
  }

  logout(firebase) {
    firebase.auth
      .signOut()
      .then(function () {
        props.naigation.navigate("Login");
      })
      .catch(function (err) {});
  }

  render() {
    return (
      <View style={styles.container}>
        <DrawerContentScrollView {...this.props}>
          <View style={styles.menu}>
            <Text style={styles.menuText}>Menu</Text>
          </View>

          <View style={styles.profileName}>
            <FirebaseContext.Consumer>
              {(firebase) =>
                firebase && (
                  <View style={styles.textsTitle}>
                    <Text style={styles.nameText}>
                      {firebase.getUsername()}
                    </Text>
                    <Text style={styles.emailText}>
                      {firebase.getUserEmail()}
                    </Text>
                  </View>
                )
              }
            </FirebaseContext.Consumer>
          </View>

          <View style={styles.screens}>
            <View style={styles.drawerItemView}>
              <Icon
                name="ios-person"
                style={styles.icon1}
                size={normalize(21)}
              />
              <DrawerItem
                style={styles.drawerItem2}
                labelStyle={styles.fontStyle}
                label="Perfil"
                onPress={() => {
                  this.props.setScreen("profile");
                }}
              />
            </View>

            <View style={styles.drawerItemView}>
              <EntypoIcon
                name="bar-graph"
                style={styles.icon}
                size={normalize(20)}
              />
              <DrawerItem
                style={styles.drawerItem}
                labelStyle={styles.fontStyle}
                label="Dashboard"
                onPress={() => {
                  this.props.navigation.navigate("Dashboard");
                }}
              />
            </View>

            <View style={styles.drawerItemView}>
              <EntypoIcon
                name="wallet"
                style={styles.icon}
                size={normalize(20)}
              />
              <DrawerItem
                style={styles.drawerItem}
                labelStyle={styles.fontStyle}
                label="Carteira"
                onPress={() => {
                  this.props.navigation.navigate("Wallet");
                }}
              />
            </View>

            <View style={styles.drawerItemView}>
              <Icon name="ios-mail" style={styles.icon1} size={normalize(21)} />
              <DrawerItem
                style={styles.drawerItem2}
                labelStyle={styles.fontStyle}
                label="Contato"
                onPress={() => {
                  this.props.navigation.navigate("Contact");
                }}
              />
            </View>
          </View>
        </DrawerContentScrollView>

        <View style={styles.bottom}>
          <FirebaseContext.Consumer>
            {(firebase) => (
              <View style={styles.drawerItemViewExit}>
                <Icon
                  name="ios-exit"
                  size={normalize(20)}
                  style={styles.iconExit}
                />
                <DrawerItem
                  labelStyle={styles.fontStyle}
                  label="Sair"
                  onPress={() => this.logout(firebase)}
                />
              </View>
            )}
          </FirebaseContext.Consumer>

          <View style={styles.version}>
            <Text style={styles.versionText}>Versão 1.8.3</Text>
          </View>
        </View>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 20,
    backgroundColor: "#1EBEA5",
  },

  textsTitle: {
    alignSelf: "flex-start",
    justifyContent: "flex-start",
    marginLeft: 30,
  },

  bottom: {
    position: "absolute",
    bottom: 10,
  },

  menu: {
    marginTop: 20,
    alignItems: "center",
  },

  menuText: {
    color: "#FFFFFF",
    fontWeight: "bold",
    fontFamily: "Montserrat-Bold",
    fontStyle: "normal",
    fontSize: normalize(16),
    lineHeight: normalize(20),
  },

  screens: {
    flex: 3,
    marginLeft: 20,
  },

  drawerItemView: {
    flexDirection: "row",
    alignItems: "center",
    maxHeight: isIos ? normalize(38) : normalize(45),
    justifyContent: "flex-start",
  },

  drawerItemViewExit: {
    flexDirection: "row",
    alignItems: "center",
    maxHeight: isIos ? 40 : 38,
    marginLeft: 10,
  },

  drawerItem: {
    width: 300,
    alignItems: "flex-start",
  },

  drawerItem2: {
    color: "#FFFF",
    width: 300,
  },

  fontStyle: {
    color: "#FFFF",
    fontFamily: "Montserrat-Medium",
    fontSize: normalize(15),
    lineHeight: normalize(18),
    paddingVertical: isIos ? 5 : 0,
    height: isIos ? 24 : 18,
  },

  icon: {
    color: "white",
    width: 30,
  },

  icon1: {
    color: "white",
    width: 30,
    marginLeft: 2,
  },

  iconExit: {
    color: "white",
    width: 20,
  },

  profileName: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },

  nameText: {
    color: "#FFFFFF",
    fontFamily: "Montserrat-SemiBold",
    fontStyle: "normal",
    fontSize: normalize(15),
    lineHeight: normalize(18),
  },

  emailText: {
    color: "#FFFFFF",
    fontFamily: "Montserrat-Regular",
    fontStyle: "normal",
    fontSize: normalize(12),
    lineHeight: normalize(18),
    // alignSelf: 'center',
  },

  version: {
    marginLeft: normalize(20),
  },

  versionText: {
    color: "#FFFFFF",
    fontFamily: "Montserrat-Regular",
    fontStyle: "normal",
    fontSize: normalize(10),
  },
});
