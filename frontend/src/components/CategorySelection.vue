<template>
  <div class="container-3">

    <div class="title">Category</div>
    <div class = "combobox">
      <select id="selected-category" v-on:change="sendRequest()">
        <option v-for="category in categories" v-bind:key="category.id">{{category}}</option>
      </select>
    </div>
    <div class="title-2">Number of Tweets : {{this.nb_tweets}}</div>         
  </div>
</template>

<script>
  import $ from 'jquery'
  import {eventBus} from "../main.js"

  export default {
    name: 'CategorySelection',
    data: function() {
      return {
        'current_category' : 'All',
        'categories' : ['All','Business', 'Food', 'Health', 'Politics', 'Science', 'Sports', 'Tech', 'Travel'],
        'nb_tweets':0
      }
    },

     methods : {
      sendRequest: function () {
        //Save the parameters
        this.current_category = document.getElementById("selected-category").value;
        //Prepare the json object that will serve as the HTTP POST Request's body
        var request_body = JSON.stringify(
        {
          "category":this.current_category
        })
        var vm = this;
        //Launch the HTTP POST Request to the server
        $.post( "http://127.0.0.1:8000/category/", request_body)
            .done(function( data) {
              console.log( "[CategorySelection] Data Loaded: " + JSON.stringify(data) );
              data = JSON.parse(data);
              vm.nb_tweets = data['count'];
              console.log("nb_tweets = "+vm.nb_tweets);
              eventBus.$emit('launchTopicAnalysis');
            });      
      },
    },

    created() {
      eventBus.$on('launchDefaultAnalysis', function() {
        this.sendRequest();
      })
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .container-3 {
    display:flex;
    padding:20px;
  }

  .title {
    color:#4786A9;
    font-size:20px;
    padding-right:20px;
  }

  .title-2 {
    color:#4786A9;
    font-size:20px;
    padding-right:20px;
    padding-left:30px;
  }

  .combobox select {
    width:150px;
    height:30px;
    background-color:#EEEEEE;
    border: transparent;
    border-radius:6px;
  } 


</style>
