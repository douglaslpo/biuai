import React from 'react';
import {StyleSheet, TouchableOpacity, Text} from 'react-native';

const Button = (props) => {
    return(
        <TouchableOpacity onPress={props.onPress} style={styles.touchableOpacity}>
            <Text style={styles.text}>{props.text}</Text>
        </TouchableOpacity>
    );
}

const styles = StyleSheet.create({
    touchableOpacity: {
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#1EBEA5',
        borderRadius: 100,
        borderWidth: 2,
        borderColor: "#00E1B5",
        marginTop: 20,
        minWidth: 143,
        maxHeight: 36
    },
    text: {
        alignSelf: 'center',
        paddingLeft: 30,
        paddingRight: 30,
        paddingTop: 15,
        paddingBottom: 15,
        color: '#fff',
        fontSize: 12,
    }
});

export default Button;