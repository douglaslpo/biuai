import React, { Component } from 'react';
import { View, Text, StyleSheet } from 'react-native';

class Title extends Component {
  constructor(props) {
    super(props);
    this.state = {
    };
  }

  render() {
    return (
      <View style={styles.titleView}>
        <Text style={styles.title}>{this.props.title}</Text>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  titleView: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },

  title: {
    fontWeight: 'bold',
    fontSize: 12,
    lineHeight: 15,
    color: '#343F53',
    fontFamily: 'Montserrat-Medium'
  },
});

export default Title;