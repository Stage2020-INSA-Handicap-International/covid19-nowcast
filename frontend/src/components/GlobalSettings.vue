<template>
  <div class="container-2">

    <div class="title">Country</div>
    <div class = "combobox">
      <select id="selected-country">
        <option>-- Select a Country --</option>
        <option v-for="country in countries" v-bind:key="country.id">{{country}}</option>
      </select>
    </div>

    <div class="title">Source</div>
    <div class = "combobox">
      <select id="selected-source">
        <option> Twitter </option>
        <option v-for="source in sources" v-bind:key="source.id">{{source}}</option>
      </select>
    </div> 

    <div class="title">Language</div>
    <div class = "combobox">
      <select id="selected-language">
        <option>-- Select a Language --</option>
        <option v-for="language in languages" v-bind:key="language.id">{{language}}</option>
      </select>
    </div>     

    <div class="title">From</div>
    <div class = "combobox"><input id="selected-start-date" type="date"></div>

    <div class="title">To</div>
    <div class = "combobox"><input id="selected-end-date" type="date"></div>

    <div class="title">Tweets</div>
    <div class = "combobox2"><input id="selected-nb-tweets" type="number" value="100" min="10" step="10"></div>    

    <button v-on:click="sendRequest()"><p class="title-2">LAUNCH ANALYSIS</p></button>
    <!--<button v-on:click="get()">GET</button>-->           
  </div>
</template>

<script>
//import axios from 'axios'
import $ from 'jquery'
import {eventBus} from "../main.js"

export default {
  name: 'GlobalSettings',

  data: function() {
    return {
      'selected_country' : '', 
      'selected_source' : '', 
      'selected_language' : '', 
      'selected_start_date' : '', 
      'selected_end_date' : '', 
      'server_response' : [],
      'selected_nb_tweets':100,

      'sources' : [],
      'languages' : ["English","French"],
      'countries' : ['Afghanistan', 'Algeria', 'Bangladesh', 'Belgium', 'Benin', 'Bolivia', 'Burkina Faso', 'Cambodia', 'Canada', 'Cape Verde', 'Central African Republic', 'Chad', 'China', 'Colombia', 'Cuba', 'Egypt', 'Ethiopia', 'France', 'Germany', 'Guinea-Bissau', 'Haiti', 'India', 'Indonesia', 'Iraq', 'Jordan', 'Kenya', 'Lao PDR', 'Lebanon', 'Libya', 'Luxembourg', 'Madagascar', 'Mali', 'Morocco', 'Mozambique', 'Myanmar', 'Nepal', 'Niger', 'Pakistan', 'Philippines', 'Rwanda', 'Senegal', 'Sierra Leone', 'Somalia', 'South Sudan', 'Sri Lanka', 'Switzerland', 'Thailand', 'Togo', 'Tunisia', 'United Kingdom', 'United States of America', 'Viet Nam', 'Yemen'].sort()

    }
  },

  methods : {
    sendRequest: function () {
      //Save the parameters
      this.selected_country = document.getElementById("selected-country").value;
      this.selected_source = document.getElementById("selected-source").value.toLowerCase();
      this.selected_language = document.getElementById("selected-language").value;
      this.selected_start_date = document.getElementById("selected-start-date").value;
      this.selected_end_date = document.getElementById("selected-end-date").value;

      var lang_converter = {'French':'fr','English':'en'};
      this.selected_language = lang_converter[this.selected_language];

      var input_nb_tweets = document.getElementById("selected-nb-tweets").value;
      this.selected_nb_tweets = parseInt(input_nb_tweets,10);
      console.log('selected_nb_tweets '+this.selected_nb_tweets)
      //Prepare the json object that will serve as the HTTP POST Request's body
      var request_body = JSON.stringify(
      {
        "country":this.selected_country,
        "source":this.selected_source,
        "lang":this.selected_language,
        "date_from":this.selected_start_date,
        "date_to":this.selected_end_date,
        "count":this.selected_nb_tweets
      })

      //Launch the HTTP POST Request to the server    
      $.post( "http://0.0.0.0:8000/collector/", request_body)
          .done(function( data) {
            alert( "[GlobalSettings]Data Loaded: " + JSON.stringify(data) );
            eventBus.$emit('launchDefaultAnalysis');

          });        
      
      
    },
    get: function () {
      //Launch the HTTP POST Request to the server
      $.get( "http://0.0.0.0:8000/access/")
          .done(function( data ) {
            alert( "Data Loaded: " + JSON.stringify(data) );
          });      
    },    
  },

};





</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .container-2 {
    display:flex;
    justify-content:space-between;
    background-color: #5D9DC1;
    padding:20px;
  }

  .title {
    color:white;
    font-size:20px;
  }

  .title-2 {
    padding:10px;
  }

  .combobox select, input {
    width:150px;
    height:30px;
    background-color:#EEEEEE;
    border: transparent;
    border-radius:6px;
    text-align:center;
  } 

  .combobox2 input {
    width:50px;
    height:30px;
    background-color:#EEEEEE;
    border: transparent;
    border-radius:6px;
    text-align:center;
  }  

  button {
    background-color:#FFFFFF;
    font-weight:bold;
    color:#5D9DC1;
    border: transparent;
    border-radius:6px;
    margin-left:15px;
  }

  select, textarea {
    font-size:13px;
    padding-left:5px;
    padding-right:5px;
  }

  input[type="date"], textarea {
    text-align: center;
    font-size:13px;
    padding-left:5px;
    padding-right:5px;
  }


</style>
