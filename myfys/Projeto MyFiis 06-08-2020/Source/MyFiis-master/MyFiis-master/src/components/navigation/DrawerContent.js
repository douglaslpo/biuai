import React, { useState } from "react";
import { View, Text, StyleSheet, Button } from "react-native";
import Menu from "./Menu";
import Profile from "./Profile";

export function DrawerContent(props) {
  const [screen, setScreen] = useState("sidemenu");

  const loadScreen = () => {
    switch (screen) {
      case "sidemenu":
        return <Menu {...props} setScreen={setScreen} />;
      case "profile":
        return <Profile {...props} setScreen={setScreen} />;
    }
  };

  return <>{loadScreen()}</>;
}

const styles = StyleSheet.create({});
