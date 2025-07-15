import React, { Component } from "react";
import { View, Text, StyleSheet } from "react-native";
import ActionButton from "react-native-action-button";
// import Icon from 'react-native-vector-icons/Ionicons';
import Icon from "react-native-vector-icons/FontAwesome";
import { useNavigation } from "@react-navigation/native";
import LinearGradient from "react-native-linear-gradient";
import { normalize } from "../../../lib/normalize";
class NewActionButton extends Component {
  constructor(props) {
    super(props);
  }

  renderDirectAccess() {
    return (
      <ActionButton
        buttonColor="#00E1B5"
        position="right"
        offsetX={10}
        offsetY={0}
        size={normalize(52)}
        spacing={normalize(12)}
        onPress={() =>
          this.props.navigation.navigate(this.props.directAccess.route, {
            action: this.props.directAccess.action,
            fiiOrigin: this.props.directAccess.extraData.fiiOrigin,
          })
        }
      ></ActionButton>
    );
  }

  render() {
    if (this.props.directAccess && this.props.directAccess.route) {
      return this.renderDirectAccess();
    }

    return (
      <ActionButton
        buttonColor="#00E1B5"
        position="right"
        spacing={normalize(12)}
        size={normalize(52)}
      >
        <ActionButton.Item
          buttonColor="#00E1B5"
          onPress={() =>
            this.props.navigation.navigate("ApplicationDetail", {
              action: "add",
            })
          }
        >
          <Icon name="sticky-note" style={styles.actionButtonIcon} />
        </ActionButton.Item>
        <ActionButton.Item
          buttonColor="#00E1B5"
          onPress={() =>
            this.props.navigation.navigate("DividendDetail", { action: "add" })
          }
        >
          <Icon name="dollar" style={styles.actionButtonIcon} />
        </ActionButton.Item>
      </ActionButton>
    );
  }
}

const styles = StyleSheet.create({
  actionButtonIcon: {
    fontSize: normalize(20),
    height: normalize(22),
    color: "#FFFF",
  },
});

// Wrap and export
export default function (props) {
  const navigation = useNavigation();

  return <NewActionButton {...props} navigation={navigation} />;
}
