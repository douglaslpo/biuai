import React from "react";
import { View, Input, StyleSheet, TextInput } from "react-native";
// import { Icon } from 'react-native-elements';
import Icon from "react-native-vector-icons/Feather";
import KeyIcon from "../../common/svgs/KeyIcon";

const InputPassword = (props) => {
  const iconStyle = () => {
    let style = {
      marginBottom: 5,
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
      alignItems: "center",
      borderRadius: 100,
      borderWidth: 2,
      maxHeight: 70,
      maxWidth: 265,
      paddingLeft: 20,
      margin: 8,
      marginTop: 0,
      borderColor: props.failed === false ? "#E0E0E0" : "red",
    };

    return style;
  };

  const textInputStyle = () => {
    let style = {
      flex: 1,
      padding: 10,
      width: "56%",
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
      <KeyIcon style={iconStyle()} />
      {/* <Icon style={iconStyle()} name="lock" size={20} color="#000" /> */}
      <TextInput
        value={props.value}
        secureTextEntry={true}
        autoCompleteType="password"
        style={textInputStyle()}
        onChangeText={props.onChange}
        placeholder="Senha *"
      />
      {/* <Icon style={eyeStyle()} name="remove-red-eye" size={20} color="#000" /> */}
    </View>
  );
};

const styles = StyleSheet.create({});

export default InputPassword;
