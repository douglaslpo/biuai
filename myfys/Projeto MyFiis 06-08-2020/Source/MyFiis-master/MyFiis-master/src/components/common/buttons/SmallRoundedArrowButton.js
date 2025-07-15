import React from 'react';
import {TouchableOpacity, Text, StyleSheet, Icon} from 'react-native';

const SmallRoundedArrowButton = (props) => {
    return(
       <TouchableOpacity onPress={props.onPress}>
           <Text style={styles.touchable}>
               Confirmar
           </Text>
           {/* <Icon name="forward" /> */}
       </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    touchable: {
        padding: 10,
        color: '#1EBEA5',
        fontWeight: 'bold',
        alignSelf: 'flex-end',
        marginRight: 10,
        marginBottom: 10,
        paddingTop: 15,
        fontSize: 15
    },
});

export default SmallRoundedArrowButton;