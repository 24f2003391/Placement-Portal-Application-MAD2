<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/authStore'
import { useMessageStore } from '@/stores/messageStore'

const router = useRouter()

const authStore = useAuthStore()
const messageStore = useMessageStore()

const loading = ref(false)
const submitting = ref(false)

const programs = ref([])

const form = ref({
  job_title: '',
  job_description: '',
  application_deadline: '',
  eligibility: [
    {
      program_code: '',
      min_cgpa: '',
      eligible_year: ''
    }
  ]
})

async function fetchPrograms() {

  loading.value = true

  try {

    const res = await fetch(
      'http://127.0.0.1:5000/api/programs'
    )

    const data = await res.json()

    if (!res.ok) {

      messageStore.updateMessages(
        data.message || 'Unable to fetch programs',
        'danger'
      )

      return

    }

    programs.value = data

  }
  catch (err) {

    console.error(err)

    messageStore.updateMessages(
      'Unable to connect to server',
      'danger'
    )

  }
  finally {

    loading.value = false

  }

}

function addEligibility() {

  form.value.eligibility.push({
  program_code: '',
  min_cgpa: '',
  eligible_year: ''
})

}

function removeEligibility(index) {

  if (form.value.eligibility.length === 1)
    return

  form.value.eligibility.splice(index, 1)

}

async function submitDrive() {

    if (!form.value.job_title.trim()) {
    messageStore.updateMessages('Job title is required.', 'danger')
    return
    }

    if (!form.value.job_description.trim()) {
    messageStore.updateMessages('Job description is required.', 'danger')
    return
    }

    if (!form.value.application_deadline) {
    messageStore.updateMessages('Application deadline is required.', 'danger')
    return
    }

    for (const item of form.value.eligibility) {
    if (!item.program_code || !item.min_cgpa || !item.eligible_year) {
        messageStore.updateMessages(
        'Please complete all eligibility fields.',
        'danger'
        )
        return
    }
    }

    submitting.value = true

    try {

    const res = await fetch(

      'http://127.0.0.1:5000/api/company/drives',

      {

        method: 'POST',

        headers: {

          'Content-Type': 'application/json',

          Authorization: authStore.token

        },

        body: JSON.stringify(form.value)

      }

    )

    const data = await res.json()

    if (!res.ok) {

      messageStore.updateMessages(
        data.message || 'Unable to create drive',
        'danger'
      )

      return

    }

    messageStore.updateMessages(
      data.message,
      'success'
    )

    router.push('/company/placement-drives')

  }

  catch (err) {

    console.error(err)

    messageStore.updateMessages(
      'Server Error',
      'danger'
    )

  }

  finally {

    submitting.value = false

  }

}

function cancel() {

  router.push('/company/placement-drives')

}

onMounted(fetchPrograms)
</script>

<template>

<div class="container mt-4">

  <h2>Create Placement Drive</h2>

  <div
    v-if="loading"
    class="text-center mt-5">

    <div class="spinner-border"></div>

  </div>

  <div
    v-else
    class="card shadow-sm">

    <div class="card-body">

      <!-- Job Title -->

      <div class="mb-3">

        <label class="form-label">
          Job Title
        </label>

        <input
          type="text"
          class="form-control"
          v-model="form.job_title"
          placeholder="Software Engineer">

      </div>

      <!-- Description -->

      <div class="mb-3">

        <label class="form-label">
          Job Description
        </label>

        <textarea
          rows="6"
          class="form-control"
          v-model="form.job_description"
          placeholder="Describe the job responsibilities...">
        </textarea>

      </div>

      <!-- Deadline -->

      <div class="mb-4">

        <label class="form-label">
          Application Deadline
        </label>

        <input
          type="datetime-local"
          class="form-control"
          v-model="form.application_deadline">

      </div>

      <hr>

      <!-- Eligibility -->

      <div class="d-flex justify-content-between align-items-center mb-3">

        <h4 class="mb-0">

          Eligibility Criteria

        </h4>

        <button
          class="btn btn-success btn-sm"
          @click="addEligibility">

          + Add Eligibility

        </button>

      </div>

      <!-- Eligibility Cards -->

      <div
        v-for="(item,index) in form.eligibility"
        :key="index"
        class="card mb-3 border-primary">

        <div
          class="card-header d-flex justify-content-between align-items-center">

          <strong>

            Eligibility {{ index+1 }}

          </strong>

          <button
            class="btn btn-outline-danger btn-sm"
            @click="removeEligibility(index)"
            :disabled="form.eligibility.length==1">

            Remove

          </button>

        </div>

        <div class="card-body">

          <div class="row">

            <!-- Program -->

            <div class="col-md-4 mb-3">

              <label class="form-label">

                Program

              </label>

              <select
                class="form-select"
                v-model="item.program_code">

                <option value="">

                  Select Program

                </option>

                <option
                  v-for="program in programs"
                  :key="program.code"
                  :value="program.code">

                  {{ program.code }} - {{ program.name }}

                </option>

              </select>

            </div>

            <!-- CGPA -->

            <div class="col-md-4 mb-3">

              <label class="form-label">

                Minimum CGPA

              </label>

              <input
                type="number"
                step="0.01"
                min="0"
                max="10"
                class="form-control"
                v-model="item.min_cgpa">

            </div>

            <!-- Year -->

            <div class="col-md-4 mb-3">

              <label class="form-label">

                Eligible Year

              </label>

              <input
                type="number"
                min="1"
                class="form-control"
                v-model="item.eligible_year">

            </div>

          </div>

        </div>

      </div>

      <!-- Buttons -->

      <div class="mt-4 text-end">

        <button
          class="btn btn-secondary me-2"
          @click="cancel">

          Cancel

        </button>

        <button
          class="btn btn-primary"
          @click="submitDrive"
          :disabled="submitting">

          <span
            v-if="submitting"
            class="spinner-border spinner-border-sm me-2">
          </span>

          Create Placement Drive

        </button>

      </div>

    </div>

  </div>

</div>

</template>