<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'

const router = useRouter()

const authStore = useAuthStore()
const messageStore = useMessageStore()

const loading = ref(false)

const drives = ref([])

const filters = ref({
  company: '',
  job_title: '',
  deadline: ''
})

async function fetchDrives() {

  loading.value = true

  try {

    const params = new URLSearchParams()

    if (filters.value.company)
      params.append('company', filters.value.company)

    if (filters.value.job_title)
      params.append('job_title', filters.value.job_title)

    if (filters.value.deadline)
      params.append('deadline', filters.value.deadline)

    const res = await fetch(
      `http://127.0.0.1:5000/api/student/placement-drives?${params.toString()}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: authStore.token
        }
      }
    )

    const data = await res.json()

    if (!res.ok) {

      messageStore.updateMessages(
        data.message || 'Failed to load placement drives.',
        'danger'
      )

      return
    }

    drives.value = data.drives

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

function clearFilters() {

  filters.value.company = ''
  filters.value.job_title = ''
  filters.value.deadline = ''

  fetchDrives()

}

function viewDrive(id) {

  router.push(`/student/placement-drives/${id}`)

}

onMounted(fetchDrives)
</script>

<template>

<div class="container mt-4">

  <div class="d-flex justify-content-between align-items-center mb-4">

    <div>

      <h2>

        Browse Placement Drives

      </h2>

      <p class="text-muted mb-0">

        Search and apply for available placement drives.

      </p>

    </div>

  </div>

  <div class="card shadow-sm mb-4">

    <div class="card-header">

      <strong>

        Search

      </strong>

    </div>

    <div class="card-body">

      <div class="row">

        <div class="col-md-4 mb-3">

          <label class="form-label">

            Company Name

          </label>

          <input
            v-model="filters.company"
            class="form-control"
            type="text"
            placeholder="Enter company name">

        </div>

        <div class="col-md-4 mb-3">

          <label class="form-label">

            Job Title

          </label>

          <input
            v-model="filters.job_title"
            class="form-control"
            type="text"
            placeholder="Enter job title">

        </div>

        <div class="col-md-4 mb-3">

          <label class="form-label">

            Apply Before

          </label>

          <input
            v-model="filters.deadline"
            class="form-control"
            type="date">

        </div>

      </div>

      <div class="text-end">

        <button
          class="btn btn-secondary me-2"
          @click="clearFilters">

          Clear

        </button>

        <button
          class="btn btn-primary"
          @click="fetchDrives">

          Search

        </button>

      </div>

    </div>

  </div>

  <div
    v-if="loading"
    class="text-center mt-5">

    <div class="spinner-border"></div>

  </div>

  <div
    v-else
    class="card shadow-sm">

    <div class="card-header">

      <strong>

        Available Placement Drives

      </strong>

    </div>

    <div class="card-body">

      <table class="table table-hover align-middle">

        <thead>

          <tr>

            <th>Company</th>
            <th>Job Title</th>
            <th>Application Deadline</th>
            <th>Action</th>

          </tr>

        </thead>

        <tbody>

          <tr
            v-for="drive in drives"
            :key="drive.id">

            <td>

              {{ drive.company }}

            </td>

            <td>

              {{ drive.job_title }}

            </td>

            <td>

              {{ drive.application_deadline }}

            </td>

            <td>

              <button
                class="btn btn-sm btn-outline-primary"
                @click="viewDrive(drive.id)">

                View

              </button>

            </td>

          </tr>

          <tr
            v-if="drives.length===0">

            <td
              colspan="4"
              class="text-center">

              No placement drives found.

            </td>

          </tr>

        </tbody>

      </table>

    </div>

  </div>

</div>

</template>