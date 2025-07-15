import React from 'react';
import {View, ActivityIndicator} from 'react-native';

const Spinner = ({size}) => {
    return(
        <View style={styles.container} >
            <ActivityIndicator size={size}/>
        </View>
    );
};

const styles = {
    // container: {
    //     flex: 1,
    //     justifyContent: 'center',
    //     alignItems: 'center'
    // }
};

export default Spinner;