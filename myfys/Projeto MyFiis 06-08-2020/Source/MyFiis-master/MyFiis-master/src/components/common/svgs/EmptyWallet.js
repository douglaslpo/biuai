import * as React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import Svg, { Path } from "react-native-svg";

class EmptyWallet extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    return (
      <>
        <View style={styles.container}>
          <Svg
            width={67}
            height={55}
            viewBox="0 0 67 55"
            fill="none"
            {...this.props}
          >
            <Path
              fillRule="evenodd"
              clipRule="evenodd"
              d="M2.744 11.012L52.459 2.15c.98-.175 1.901.568 2.058 1.658l.001.007 4.864 34.554c.153 1.09-.514 2.11-1.491 2.285L8.175 49.516c-.98.175-1.9-.568-2.058-1.659v-.006L1.253 13.296c-.153-1.088.514-2.11 1.491-2.284z"
              fill="#fff"
            />
            <Path
              d="M55.181 10.384c.11.795.204 1.491.286 2.089M10.763 48.949l-1.906.35c-1.31.24-2.539-.795-2.746-2.312L1.605 14.026c-.208-1.517.686-2.941 1.995-3.182l48.01-8.81c1.31-.24 2.539.795 2.746 2.312l.483 3.534L10.763 48.95z"
              stroke="#26BFBD"
              strokeWidth={2.5}
              strokeLinecap="round"
            />
            <Path
              fillRule="evenodd"
              clipRule="evenodd"
              d="M5.154 12.528l45.365-7.887c.977-.17 1.894.571 2.051 1.658l4.407 30.547c.158 1.09-.509 2.116-1.488 2.291a.176.176 0 01-.008.002l-45.366 7.887c-.977.17-1.893-.572-2.05-1.659L3.657 14.821c-.157-1.09.51-2.117 1.49-2.292l.007-.001z"
              fill="#E8F0FE"
            />
            <Path
              d="M63.102 15.5H16.096c-1.323 0-2.395 1.194-2.395 2.667V50.5c0 1.473 1.072 2.667 2.395 2.667h47.006c1.323 0 2.395-1.194 2.395-2.667V18.167c0-1.473-1.072-2.667-2.395-2.667z"
              fill="#fff"
              stroke="#26BFBD"
              strokeWidth={2.5}
            />
            <Path d="M64.749 23.333h-50.3v9.334h50.3v-9.334z" fill="#E8F0FE" />
            <Path
              clipRule="evenodd"
              d="M65.15 23.333H25.725 65.15zM61.558 32h-47.21 47.21zM35.744 44.667h-16.95 16.95zM22.706 23.333h-4.31 4.31z"
              stroke="#26BFBD"
              strokeWidth={2.5}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </Svg>

          <Text style={styles.message}>
            Ainda não há registros em sua carteira.
          </Text>

          <Text style={styles.message}>Adicione sua primeira aplicação.</Text>

          <View style={styles.addContainer}>
            <TouchableOpacity
              style={styles.add}
              onPress={() =>
                this.props.navigation.navigate("ApplicationDetail", {
                  action: "add",
                })
              }
            >
              <Text style={{ color: "#FFFFFF" }}>Adicionar</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.container}></View>
      </>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    marginTop: 20,
  },

  message: {
    paddingTop: 10,
  },

  addContainer: {
    marginTop: 10,
    justifyContent: "center",
    alignItems: "center",
  },

  add: {
    height: 30,
    width: 150,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#26BFBD",
    borderRadius: 10,
  },
});

export default EmptyWallet;
