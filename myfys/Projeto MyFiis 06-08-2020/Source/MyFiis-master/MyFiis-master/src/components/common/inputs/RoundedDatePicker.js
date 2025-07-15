import React from 'react';
import { View, StyleSheet, TextInput, Text } from 'react-native';
import DatePicker from 'react-native-datepicker'


const RoundedDatePicker = (props) => {

    const renderLabel = () => {
        if (props.label) {
            return <Text style={styles.label}>{props.label}</Text>
        }
    };

    const type = props.type ? props.type : 'off';
    const autocomplete = props.autocomplete ? props.autocomplete : 'off';
    const keyboardType = props.keyboardType ? props.keyboardType : "email-address";
    const autoFocus = props.autoFocus ? true : false
    const secureTextEntry = props.secureTextEntry ? true : false;


    return (
        <>
            {renderLabel()}

            <View style={styles.viewInput}>

                <DatePicker
                    placeholderTextColor="#DADADA"
                    style={styles.textInput}
                    onDateChange={props.onChange}
                    placeholder={props.placeholder}
                    label={props.label}
                    secureTextEntry={secureTextEntry}
                    autoCompleteType={autocomplete}
                    type={type}
                    autoCorrect={false}
                    keyboardType={keyboardType}
                    autoFocus={autoFocus}
                    date={props.date}
                    mode="date"
                    format="DD/MM/YYYY"
                    minDate="01/01/1993"
                    maxDate="01/01/2110"
                    confirmBtnText="Confirmar"
                    cancelBtnText="Cancelar"
                    showIcon={false}
                    textAlign="center"

                    customStyles={{
                        dateInput: {
                            borderWidth: 0,
                        },
                        dateText: {
                            flex: 1,
                            marginTop: 12,
                            borderRadius: 15,
                            color: '#222222',
                            fontFamily: 'Montserrat-Medium',
                            lineHeight: 15,
                            fontSize: 12,
                        },
                        placeholderText: {
                            fontSize: 12,
                            fontWeight: '900',

                        }
                    }}
                />
            </View>
        </>
    );
}

const styles = StyleSheet.create({

    label: {
        alignSelf: 'flex-start',
        marginLeft: 15,
        marginTop: 15,
        color: '#343F53'
    },

    viewInput: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'flex-start',
        borderRadius: 30,
        borderColor: "#9b9b9b",
        borderWidth: 0.5,
        maxHeight: 40,
        marginTop: 5
    },

    textInput: {
        flex: 1,
        padding: 5,
        borderRadius: 15,
        fontSize: 12,
        lineHeight: 15,
        fontWeight: '100',
        marginHorizontal: 10,
        marginVertical: 5,
    },

    iconInput: {
        padding: 10,
        color: "#9b9b9b"
    },

});

export default RoundedDatePicker;