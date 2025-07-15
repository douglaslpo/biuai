import React, { Component } from "react";
import { View, Text } from "react-native";
import AwesomeAlert from "react-native-awesome-alerts";

export default class Alert extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    const confirmText = this.props.confirmText
      ? this.props.confirmText
      : "Estou ciente";

    return (
      <AwesomeAlert
        show={this.props.show}
        showProgress={false}
        title={this.props.title}
        message={this.props.message}
        closeOnTouchOutside={true}
        closeOnHardwareBackPress={false}
        showCancelButton={false}
        showConfirmButton={true}
        confirmText={confirmText}
        confirmButtonColor="#1EBEA5"
        onCancelPressed={this.props.onCancel}
        onConfirmPressed={this.props.onConfirm}
      />
    );
  }
}
