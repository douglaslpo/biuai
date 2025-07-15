import "react-native-gesture-handler";
import React, { useEffect, useState } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from "@react-navigation/stack";
import { createDrawerNavigator } from "@react-navigation/drawer";
import { DrawerContent } from "./src/components/navigation/DrawerContent";

import Firebase, { FirebaseContext } from "./src/components/firebase";

import LoginScreen from "./src/screens/Login/LoginScreen";
import NewUserScreen from "./src/screens/Login/NewUserScreen";
import ForgotPasswordScreen from "./src/screens/Login/ForgotPasswordScreen";
import WalletScreen from "./src/screens/Wallet/WalletScreen";
import DashboardScreen from "./src/screens/Dashboard/DashboardScreen";
import ApplicationsScreen from "./src/screens/Applications/ApplicationsScreen";
import ApplicationDetailScreen from "./src/screens/Applications/ApplicationDetailScreen";
import DividendsScreen from "./src/screens/Dividends/DividendsScreen";
import DividendDetailScreen from "./src/screens/Dividends/DividendDetailScreen";
import ContactScreen from "./src/screens/Contact/ContactScreen";
import { YellowBox } from "react-native";

import SplashScreen from "react-native-splash-screen";

const Stack = createStackNavigator();
const Drawer = createDrawerNavigator();

function UserArea() {
  return (
    <Drawer.Navigator
      drawerContentOptions={{
        activeTintColor: "#FFFFFF",
        contentContainerStyle: {
          backgroundColor: "#1EBEA5",
          height: "100%",
        },
        itemStyle: {},
        labelStyle: {
          color: "#FFFFFF",
        },
        title: "Menu",
      }}
      sceneContainerStyle={{
        backgroundColor: "#FFFFF",
      }}
      drawerContent={(props) => <DrawerContent {...props} />}
    >
      <Drawer.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{ title: "Dashboard" }}
      />
      <Drawer.Screen
        name="Wallet"
        component={WalletScreen}
        options={{ title: "Carteira" }}
      />
      <Drawer.Screen
        name="Applications"
        component={ApplicationsScreen}
        options={{ title: "Aplicações" }}
      />
      <Drawer.Screen
        name="ApplicationDetail"
        component={ApplicationDetailScreen}
        options={{ title: "Adicionar Aplicações" }}
      />
      <Drawer.Screen
        name="Dividends"
        component={DividendsScreen}
        options={{ title: "Dividendos" }}
      />
      <Drawer.Screen
        name="DividendDetail"
        component={DividendDetailScreen}
        options={{ title: "Adicionar Dividendos" }}
      />
      <Drawer.Screen
        name="Contact"
        component={ContactScreen}
        options={{ title: "Contato" }}
      />
    </Drawer.Navigator>
  );
}

function App() {
  const [firebase, setFirebase] = useState(null);

  useEffect(() => {
    load = async () => {
      try {
        let fire = new Firebase();
        await fire.settings();
        await fire.loadFiisList();
        setFirebase(fire);
      } catch (e) {
        console.log("Error pro settings  firebase", e);
      }
      SplashScreen.hide();
    };

    load();
  }, []);

  if (firebase != null) {
    return (
      <FirebaseContext.Provider value={firebase}>
        <NavigationContainer>
          <Stack.Navigator
            initialRouteName="UserArea"
            screenOptions={{
              headerShown: false,
            }}
          >
            <Stack.Screen name="UserArea" component={UserArea} />
            <Stack.Screen
              name="Login"
              component={LoginScreen}
              options={{ title: "Login" }}
            />
            <Stack.Screen
              name="NewUser"
              component={NewUserScreen}
              options={{ title: "Cadastro" }}
            />
            <Stack.Screen
              name="ForgotPassword"
              component={ForgotPasswordScreen}
              options={{ title: "Esqueceu a senha" }}
            />
          </Stack.Navigator>
        </NavigationContainer>
      </FirebaseContext.Provider>
    );
  } else return null;
}

YellowBox.ignoreWarnings([
  "Non-serializable values were found in the navigation state",
]);

export default App;
