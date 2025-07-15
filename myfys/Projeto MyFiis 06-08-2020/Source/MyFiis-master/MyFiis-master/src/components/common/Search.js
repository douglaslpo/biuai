import React, { Component } from 'react';
import { View, Text, TextInput, StyleSheet } from 'react-native';
import RoundedInput from './inputs/RoundedInput';

export default class Search extends Component {
  constructor(props) {
    super(props);
    this.state = {
    };
  }

  render() {
    return (
        <TextInput style={styles.textInput} placeholderTextColor="#DADADA"  placeholder="Pesquisar fundos" />
    );
  }
}

const styles = StyleSheet.create({
  textInput: {
      flex: 1,
      paddingLeft: 15,
      borderRadius: 15,
      color: 'rgba(58, 176, 162, 0.5)',
      fontWeight: 'bold',
      borderWidth: 1,
      borderColor: '#29B5A4',
      fontSize: 11,
  },
});
