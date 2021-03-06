import React, { useState } from "react";
import { StyleSheet, TouchableOpacity, View, ActivityIndicator, ScrollView, Alert } from "react-native";
import WebView from "react-native-webview";
import CText from "../components/CustomText";
import Header from "../components/Header";
import NavBar from "../components/NavBar";
import Icon from "react-native-vector-icons/Ionicons";

const CONSTANTS = require("../constants.json");

const ActivityIndicatorElement = () => {
  return (
    <ActivityIndicator
      color={CONSTANTS.darkYellow}
      size="large"
      style={styles.activityIndicatorStyle} />
  );
};

export default function Docs({ navigation, route }) {

  const CONTENT = route.params.LABELS.documentation;
  const [viewLink, setViewLink] = useState("");
  const [isLoadingVisible, setIsLoadingVisible] = useState(false);
  const handleLink = (link) => {
    setViewLink(link);
  }
  const handleGoBack = () => {
    setViewLink("");
  }
  const docLinks = {
    modelOverview: {
      name: CONTENT.modelOverview.name,
      icon: "eye",
      link: CONTENT.modelOverview.link
    },
    robotGameRulebook: {
      name: CONTENT.robotGameRulebook.name,
      icon: "ios-construct",
      link: CONTENT.robotGameRulebook.link
    },
    rubrics: {
      name: CONTENT.rubrics.name,
      icon: "checkmark-done-outline",
      link: CONTENT.rubrics.link
    },
    robotGameScoresheet: {
      name: CONTENT.robotGameScoresheet.name,
      icon: "md-shield-checkmark",
      link: CONTENT.robotGameScoresheet.link
    },
    awards: {
      name: CONTENT.awards.name,
      icon: "trophy-outline",
      link: CONTENT.awards.link
    },
    judgingSessionForTeams: {
      name: CONTENT.judgingSessionForTeams.name,
      icon: "list",
      link: CONTENT.judgingSessionForTeams.link
    },
    updates: {
      name: CONTENT.updates.name,
      icon: "md-reload-circle-outline",
      link: CONTENT.updates.link
    }
  }
  const docLinksNames = ["modelOverview", 
                          "robotGameRulebook", 
                          "rubrics", 
                          "robotGameScoresheet", 
                          "awards", 
                          "judgingSessionForTeams", 
                          "updates"]
  return (
    <View style={ styles.container }>
      <Header style={{ backgroundColor: CONSTANTS.primaryBgColor, flexDirection: "row" }}>
        { viewLink != "" ? (
          <View style={{ position: "absolute", left: 20 }}>
            <Icon name="arrow-back" size={30} color={CONSTANTS.primaryColor} onPress={handleGoBack} />
          </View>
        ):null}
        <CText style={{ fontSize: 23, color: CONSTANTS.primaryColor }}>{ CONTENT.title }</CText>
      </Header>
      <View style={{flex: 1}}>
      { viewLink ? (
          <WebView 
            style={styles.onlineDoc} 
            scalesPageToFit={false}
            containerStyle={{ position: "absolute", top: 0, width: "100%", height: "100%", zIndex: 1 }}
            renderLoading={ActivityIndicatorElement}
            startInLoadingState={true}
            source={{ html: `<iframe src="${viewLink}" width="100%" height="100%" frameborder="0" scrolling="no"></iframe>` }} />
        ): null}
      <ScrollView>
      <View style={ styles.docsContainer }>
        {
          docLinksNames.map(name => (
            <TouchableOpacity style={ styles.docContainer } onPress={() => handleLink(docLinks[name].link)} key={docLinks[name].link}>
              <Icon name={docLinks[name].icon} size={30} color={CONSTANTS.darkYellow} />
              <CText style={styles.docLink}>{docLinks[name].name}</CText>
          </TouchableOpacity> 
          ))
        }

      </View>
      </ScrollView>
      </View>
      <NavBar 
          icons={[["md-calculator-outline", "stopwatch-outline", "book-outline"],
                  ["Scorer", "Timer", "Docs"]]}
          active={[2, CONSTANTS.darkYellow]}
          pageNavigationHandler={ navigation.navigate }
          contentLabels={route.params.LABELS} />
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: CONSTANTS.primaryColor,
  },
  docContainer: {
    padding: 20,
    backgroundColor: "#fff",
    borderBottomLeftRadius: 2,
    borderBottomColor: CONSTANTS.primaryBgColor,
    borderBottomWidth: 1,

    flexDirection: "row",
    alignItems: "center",
  },
  docLink: {
    marginLeft: 10,
    color: CONSTANTS.primaryBgColor,
  },  
  activityIndicatorStyle: {
    flex: 1,
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    alignSelf: "center",
    zIndex: 2
  },
})