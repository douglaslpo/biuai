import React from "react";
import { View, StyleSheet, TextInput, Text } from "react-native";
import EmailIcon from "../../common/svgs/EmailIcon";

const InputEmail = (props) => {
  let color = "#000";
  const iconInputStyle = () => {
    let style = {
      width: 20,
      height: 20,
      marginRight: 8,
      color: props.failed === false ? "#E0E0E0" : "red",
    };

    return style;
  };

  const viewInputStyle = () => {
    let style = {
      flex: 1,
      flexDirection: "row",
      justifyContent: "center",
      alignItems: "center",
      borderRadius: 100,
      borderWidth: 2,
      maxHeight: 70,
      maxWidth: 265,
      paddingLeft: 20,
      margin: 8,
      marginTop: 10,
      borderColor: props.failed === false ? "#E0E0E0" : "red",
    };

    return style;
  };

  const textInputStyle = () => {
    let style = {
      flex: 1,
      padding: 10,
      borderRadius: 15,
      borderColor: props.failed === false ? "#000" : "red",
      color: "#1EBEA5",
      fontWeight: "500",
      fontFamily: "Montserrat-Regular",
      fontStyle: "normal",
    };

    return style;
  };

  return (
    <View style={viewInputStyle()}>
      {/* <Icon
        style={iconInputStyle()}
        name="email-outline"
        size={20}
        color={color}
      /> */}
      <EmailIcon style={iconInputStyle()} />
      <TextInput
        autoFocus={false}
        autoCompleteType="email"
        autoCorrect={false}
        keyboardType="email-address"
        style={textInputStyle()}
        onChangeText={props.onChange}
        value={props.value}
        placeholder="Email *"
        underlineColorAndroid="transparent"
      />
    </View>
  );
};

export default InputEmail;
