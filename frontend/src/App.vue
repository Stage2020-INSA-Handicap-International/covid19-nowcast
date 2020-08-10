<template>
  <div id="container-1">
    <div class = "box-1-webAppTitle"><WebAppTitle/></div>
    <div><GlobalSettings/></div>
    <div><CategorySelection/></div>
    <div><TopicAnalysis/></div>
    <div><GraphAnalysis/></div>
  </div>
</template>

<script>
import WebAppTitle from './components/WebAppTitle.vue'
import GlobalSettings from './components/GlobalSettings.vue'
import CategorySelection from './components/CategorySelection.vue'
import TopicAnalysis from './components/TopicAnalysis.vue'
import GraphAnalysis from './components/GraphAnalysis.vue'

export default {
  name: 'App',
  components: {
    WebAppTitle,
    GlobalSettings,
    CategorySelection,
    TopicAnalysis,
    GraphAnalysis
  }
}
</script>

<style>
  .container-1{
    display:flex;
    align-items:flex-start;
    flex-direction:column;
    overflow-x:auto;
  }

  .box-1-webAppTitle {
    height:200px;
  }

    div {
    font-family: 'Roboto'
  }



</style>
