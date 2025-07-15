import React, { Component } from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import Ionicons from "react-native-vector-icons/Ionicons";
import FontAwesome from "react-native-vector-icons/FontAwesome";

class ScreenHeader extends Component {
  render() {
    return (
      <View style={[styles.container, this.props.style]}>
        <View style={styles.titleContainer}>
          <Text style={styles.title}>{this.props.title}</Text>
        </View>

        {this.props.navigation ? (
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => this.props.navigation.goBack()}
          >
            <Ionicons
              name="ios-arrow-round-back"
              style={styles.iconBackButton}
            />
          </TouchableOpacity>
        ) : null}

        {this.props.deleteFunction ? (
          <TouchableOpacity
            style={styles.deleteButton}
            onPress={() => this.props.deleteFunction()}
          >
            <FontAwesome name="trash-o" style={styles.iconDeleteButton} />
          </TouchableOpacity>
        ) : null}
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    height: 60,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "flex-start",
    backgroundColor: "#FAFAFA",
  },

  titleContainer: {
    flexGrow: 1,
    flexDirection: "row",
    justifyContent: "center",
  },

  title: {
    color: "#343F53",
    fontSize: 12,
    lineHeight: 15,
    fontStyle: "normal",
    fontFamily: "Montserrat-Semibold",
  },

  backButton: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    width: 35,
    marginLeft: 10,
    position: "absolute",
  },

  iconBackButton: {
    fontSize: 30,
    color: "black",
  },

  iconDeleteButton: {
    fontSize: 24,
    color: "black",
  },

  deleteButton: {
    marginRight: 10,
  },
});

export default ScreenHeader;
