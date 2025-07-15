import React from 'react';
import {TouchableOpacity, StyleSheet, Text} from 'react-native';

const Link = (props) => {

    const to = props.to;
    
    const navigateTo = () => {
        return props.navigation.navigate(to);
    }

    return (
        <TouchableOpacity  onPress={navigateTo} style={styles.main}>
            <Text style={styles.link}>
                {props.text}
            </Text>
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    main: {
        alignSelf: 'center',
    },  
    link: {
        color: '#1EBEA5',
        alignSelf: 'center'
    }
});

export default Link;