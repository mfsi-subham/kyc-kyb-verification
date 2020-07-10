<template>
  <v-container
    id="user-profile"
    fluid
    tag="section"
  >
    <v-row justify="center">
      <v-col
        cols="12"
        md="8"
      >
        <base-material-card>
          <template v-slot:heading>
            <div class="display-2 font-weight-light">
              Upload your scanned documents for verification
            </div>
          </template>

          <v-form>
            <v-container class="py-5">
              <v-row>
                <v-col
                  cols="12"
                  md="12"
                >
                  <v-file-input
                    show-size
                    counter
                    multiple
                    label="Browse"
                    accept="image/*"
                    @change="onFileSelected"
                  />
                </v-col>

                <v-col
                  cols="12"
                  md="12"
                  class="text-right"
                >
                  <v-btn
                    color="success"
                    class="mr-0"
                    :loading="loading"
                    :disabled="disabled"
                    @click="uploadFile"
                  >
                    Upload
                  </v-btn>
                </v-col>
                <v-col
                  cols="12"
                  class="text-center"
                >
                  <v-btn
                    color="success"
                    class="mr-0"
                    :loading="loading_extract"
                    :disabled="disabled_extract"
                    @click="extractDetails"
                  >
                    Extract details from document
                  </v-btn>
                </v-col>

                <v-col
                  cols="12"
                  md="4"
                >
                  <v-text-field
                    id="form-first-name"
                    v-model="result.firstname"
                    label="First Name"
                  />
                </v-col>

                <v-col
                  cols="12"
                  md="4"
                >
                  <v-text-field
                    id="form-last-name"
                    v-model="result.surname"
                    label="Last Name"
                  />
                </v-col>

                <v-col
                  cols="12"
                  md="4"
                >
                  <v-text-field
                    id="form-passport-no"
                    v-model="result.passport_no"
                    label="Passport No"
                  />
                </v-col>

                <v-col
                  cols="12"
                  md="3"
                >
                  <v-text-field
                    id="form-country"
                    v-model="result.country"
                    label="Country"
                  />
                </v-col>

                <v-col
                  cols="12"
                  md="3"
                >
                  <v-text-field
                    id="form-sex"
                    v-model="result.sex"
                    label="sex"
                  />
                </v-col>

                <v-col
                  cols="12"
                  md="3"
                >
                  <v-text-field
                    id="form-dob"
                    v-model="result.dob"
                    label="Date of birth"
                  />
                </v-col>

                <v-col
                  cols="12"
                  md="3"
                >
                  <v-text-field
                    id="form-place-of-birth"
                    v-model="result.place_of_birth"
                    label="Place of birth"
                  />
                </v-col>

                <v-col
                  cols="12"
                  md="4"
                >
                  <v-text-field
                    id="form-place-of-issue"
                    v-model="result.place_of_issue"
                    label="Place of issue"
                  />
                </v-col>

                <v-col
                  cols="12"
                  md="4"
                >
                  <v-text-field
                    id="form-date-of-issue"
                    v-model="result.date_of_issue"
                    label="Date of issue"
                  />
                </v-col>

                <v-col
                  cols="12"
                  md="4"
                >
                  <v-text-field
                    id="form-date-of-expiry"
                    v-model="result.date_of_expiry"
                    label="Date of expiry"
                  />
                </v-col>

                <v-col
                  cols="12"
                  class="text-center"
                >
                  <v-btn
                    color="success"
                    class="mr-0"
                    :disabled="disabled_verify"
                  >
                    verify
                  </v-btn>
                </v-col>
              </v-row>
            </v-container>
          </v-form>
        </base-material-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
  import axios from 'axios'
  const uuidv1 = require('uuid/v1')
  const { BlobServiceClient } = require('@azure/storage-blob')
  const blobSasUrl = process.env.VUE_APP_AZURE_STORAGE_SAS_URL
  export default {
    name: 'KYC',
    data () {
      return {
        selectedFile: null,
        loader: null,
        loading: false,
        loading_extract: false,
        disabled: true,
        disabled_extract: true,
        blobName: null,
        jsonFileName: null,
        result: {},
        disabled_verify: true,
        errorCount: 0,
      }
    },
    methods: {
      onFileSelected (event) {
        this.selectedFile = event[0] // selecting one file
        this.disabled = false // Enabling upload button once file is selected
      },
      async uploadFile () {
        this.loading = true // start showing loading icon once upload starts
        this.disabled = true // disable the upload button till upload completes
        this.blobName = uuidv1() + '-' + this.selectedFile.name // giving image a unique name
        const containerName = 'kyc-kyb-images' // containor name
        // Uploading image file to the azure blob storage
        try {
          const blobServiceClient = new BlobServiceClient(blobSasUrl)
          const containerClient = blobServiceClient.getContainerClient(containerName)
          const blockBlobClient = containerClient.getBlockBlobClient(this.blobName)
          const file = this.selectedFile
          const promises = []
          promises.push(blockBlobClient.uploadBrowserData(file)) // upload the file
          await Promise.all(promises) // wait for completion of upload
          alert('File uploaded successfully')
          this.loading = false // stop showing loading icon
          this.disabled = false // enable the buttion
          this.disabled_extract = false // enable text extraction button
        } catch (error) {
          alert('Something went wrong')
        }
      },
      extractDetails () {
        this.jsonFileName = this.blobName.split('.')[0] + '.json' // file name for which trigger will seach in azure storage
        this.loading_extract = true // once clicked display loading icon
        this.disabled_extract = true // disable the button
        const url = 'https://kyc-kyb-json-data-extraction.azurewebsites.net/api/kyc-kyb-data-extraction-from-json/?json_file_name=' + this.jsonFileName
        axios.get(url) // get required data from api
          .then(
            (response) => {
              this.result = response.data // store the response data
              this.loading_extract = false // stop showing loading icon
            },
          ).catch(
            (error) => {
              this.errorCount = this.errorCount + 1
              // console.log(error)
              if (this.errorCount <= 5) {
                setTimeout(this.extractDetails, 2000) // continue till 5 error with 2 sec interval
              } else {
                this.error = error
              }
            },
          )
      },
    },
  }
</script>
