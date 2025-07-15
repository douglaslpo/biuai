import React from "react";
import { View, StyleSheet, TextInput, Text } from "react-native";
import { Icon } from "react-native-elements";
import { TextInputMask } from "react-native-masked-text";

const RoundedInput = (props) => {
  const renderIcon = () => {
    if (props.iconName) {
      return (
        <Icon
          iconStyle={styles.iconInput}
          name={props.iconName}
          size={props.iconSize}
          color={props.iconColor}
        />
      );
    }
  };

  const renderLabel = () => {
    if (props.label) {
      return <Text style={styles.label}>{props.label}</Text>;
    }
  };

  const type = props.type ? props.type : "off";
  const autocomplete = props.autocomplete ? props.autocomplete : "off";
  const keyboardType = props.keyboardType ? props.keyboardType : "default";
  const autoFocus = props.autoFocus ? true : false;
  const secureTextEntry = props.secureTextEntry ? true : false;
  const mask = props.mask ? props.mask : "";
  const options = props.mask ? props.options : "";

  return (
    <>
      {renderLabel()}

      <View style={styles.viewInput}>
        {renderIcon()}
        {mask ? (
          <TextInputMask
            style={styles.textInput}
            onChangeText={props.onChange}
            placeholder={props.placeholder}
            label={props.label}
            secureTextEntry={secureTextEntry}
            autoCompleteType={autocomplete}
            type={type}
            autoCorrect={false}
            keyboardType={keyboardType}
            autoFocus={autoFocus}
            options={options}
            value={props.value}
            placeholderTextColor="#DADADA"
          />
        ) : (
            <TextInput
              placeholderTextColor="#DADADA"
              style={styles.textInput}
              onChangeText={props.onChange}
              placeholder={props.placeholder}
              label={props.label}
              secureTextEntry={secureTextEntry}
              autoCompleteType={autocomplete}
              type={type}
              autoCorrect={false}
              autoFocus={autoFocus}
              keyboardType={keyboardType}
              value={props.value}
              // textAlign="center"
              textAlignVertical={"center"}
            />
          )}
      </View>
    </>
  );
};

const styles = StyleSheet.create({
  label: {
    alignSelf: "flex-start",
    fontFamily: "Montserrat-Regular",
    fontWeight: "bold",
    fontSize: 14,
    fontStyle: "normal",
    marginLeft: 8,
    marginTop: 8,
    color: "#343F53",
  },

  viewInput: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    borderRadius: 30,
    borderColor: "#9b9b9b",
    borderWidth: 0.5,
    maxHeight: 40,
    paddingLeft: 10,
    paddingRight: 10,
    margin: 5,
  },

  textInput: {
    flex: 1,
    borderRadius: 15,
    color: "#1EBEA5",
    fontWeight: "500",
    lineHeight: 15,
    fontSize: 12,
    height: 50,
    marginHorizontal: 10,
    marginVertical: 5,
  },

  iconInput: {
    padding: 10,
    color: "#9b9b9b",
  },
});

export default RoundedInput;
