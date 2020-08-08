<template>
  <div id="container-1">
    <div class = "box-1-webAppTitle"><WebAppTitle/></div>
    <div class="box-2-globalSettings"><GlobalSettings/></div>
    <div class="box-3-categorySelection"><CategorySelection/></div>
    <div class="box-4-topicAnalysisHeader"><TopicAnalysis/></div>
  </div>
</template>

<script>
import WebAppTitle from './components/WebAppTitle.vue'
import GlobalSettings from './components/GlobalSettings.vue'
import CategorySelection from './components/CategorySelection.vue'
import TopicAnalysis from './components/TopicAnalysis.vue'

export default {
  name: 'App',
  components: {
    WebAppTitle,
    GlobalSettings,
    CategorySelection,
    TopicAnalysis
  }
}
</script>

<style>
  .container-1{
    display:flex;
    align-items:flex-start;
    flex-direction:column;
  }

  .box-1-webAppTitle {
    height:200px;
  }



</style>
