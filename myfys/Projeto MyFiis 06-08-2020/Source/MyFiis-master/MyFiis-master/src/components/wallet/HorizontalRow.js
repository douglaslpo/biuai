import React, { Component } from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default class HorizontalRow extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <View style={styles.horizontalRow}>
      </View>
    );
  }
}

const styles = StyleSheet.create({
    horizontalRow: {
        borderColor: "#A6BEFF",
        borderWidth: 1,
        width: 181,
        alignSelf: 'center',
        marginTop: 15,
        marginBottom: 15
    }
});
