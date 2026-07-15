<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'

const route = useRoute()

const authStore = useAuthStore()
const messageStore = useMessageStore()

const loading = ref(false)
const submitting = ref(false)

const drive = ref({})
const eligibility = ref([])

const canApply = ref(false)
const reason = ref(null)

const resume = ref(null)

async function fetchDrive() {

  loading.value = true

  try {

    const res = await fetch(
      `http://127.0.0.1:5000/api/student/placement-drives/${route.params.id}`,
      {
        headers: {
          Authorization: authStore.token
        }
      }
    )

    const data = await res.json()

    if (!res.ok) {

      messageStore.updateMessages(
        data.message || 'Failed to load drive.',
        'danger'
      )

      return
    }

    drive.value = data.drive
    eligibility.value = data.eligibility
    canApply.value = data.can_apply
    reason.value = data.reason

  } catch (err) {

    console.error(err)

    messageStore.updateMessages(
      'Unable to connect to server.',
      'danger'
    )

  } finally {

    loading.value = false

  }

}

function selectResume(event) {

  resume.value = event.target.files[0]

}

async function apply() {

  if (!resume.value) {

    messageStore.updateMessages(
      'Please upload your resume.',
      'danger'
    )

    return

  }

  submitting.value = true

  try {

    const formData = new FormData()

    formData.append(
      'resume',
      resume.value
    )

    const res = await fetch(
      `http://127.0.0.1:5000/api/student/placement-drives/${route.params.id}/apply`,
      {
        method: 'POST',
        headers: {
          Authorization: authStore.token
        },
        body: formData
      }
    )

    const data = await res.json()

    if (!res.ok) {

      messageStore.updateMessages(
        data.message,
        'danger'
      )

      return

    }

    messageStore.updateMessages(
      data.message,
      'success'
    )

    canApply.value = false
    reason.value = 'already_applied'

  } catch (err) {

    console.error(err)

    messageStore.updateMessages(
      'Unable to connect to server.',
      'danger'
    )

  } finally {

    submitting.value = false
    resume.value = null

  }

}

function buttonText() {

  if (canApply.value)
    return 'Apply'

  switch (reason.value) {

    case 'placed':
      return 'Already Placed'

    case 'already_applied':
      return 'Already Applied'

    case 'deadline_passed':
      return 'Applications Closed'

    case 'not_eligible':
        return 'Not Eligible'

    default:
      return 'Cannot Apply'

  }

}

onMounted(fetchDrive)
</script>

<template>

<div class="container mt-4">

  <div
    v-if="loading"
    class="text-center mt-5">

    <div class="spinner-border"></div>

  </div>

  <template v-else>

    <div class="card shadow-sm">

      <div class="card-header">

        <h3>

          {{ drive.company }}

        </h3>

      </div>

      <div class="card-body">

        <h5>

          {{ drive.job_title }}

        </h5>

        <hr>

        <h6>

          Job Description

        </h6>

        <p>

          {{ drive.job_description }}

        </p>

        <hr>

        <div class="row">

          <div class="col-md-6">

            <h6>

              Company Information

            </h6>

            <p>

              <strong>Industry:</strong>
              {{ drive.industry }}

            </p>

            <p>

              <strong>Website:</strong>

              <a
                :href="drive.website"
                target="_blank">

                {{ drive.website }}

              </a>

            </p>

          </div>

          <div class="col-md-6">

            <h6>

              Application Deadline

            </h6>

            <p>

              {{ drive.application_deadline }}

            </p>

          </div>

        </div>

        <hr>

        <h6>

          Eligibility

        </h6>

        <table class="table table-bordered">

          <thead>

            <tr>

              <th>Program</th>
              <th>Minimum CGPA</th>
              <th>Eligible Year</th>

            </tr>

          </thead>

          <tbody>

            <tr
              v-for="item in eligibility"
              :key="item.id">

              <td>{{ item.program }}</td>
              <td>{{ item.min_cgpa }}</td>
              <td>{{ item.eligible_year }}</td>

            </tr>

          </tbody>

        </table>

        <hr>

        <div class="mb-4">

          <label class="form-label">

            Upload Resume (PDF)

          </label>

          <input
            class="form-control"
            type="file"
            accept=".pdf"
            @change="selectResume">

        </div>

        <button
          class="btn btn-success"
          :disabled="!canApply || submitting"
          @click="apply">

          {{ submitting ? 'Applying...' : buttonText() }}

        </button>

      </div>

    </div>

  </template>

</div>

</template>
