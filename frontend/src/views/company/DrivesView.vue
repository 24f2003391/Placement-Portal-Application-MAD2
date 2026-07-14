<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useMessageStore } from '@/stores/messageStore'

const router = useRouter()

const authStore = useAuthStore()
const messageStore = useMessageStore()

const loading = ref(false)
const drives = ref([])

const search = ref({
  job_title: '',
  status: '',
  start_date: '',
  end_date: ''
})

async function fetchDrives() {

  loading.value = true

  try {

    const params = new URLSearchParams()

    Object.entries(search.value).forEach(([key, value]) => {
      if (value) params.append(key, value)
    })

    const res = await fetch(
      `http://127.0.0.1:5000/api/company/drives?${params.toString()}`,
      {
        method: 'GET',
        headers: {
          Authorization: authStore.token
        }
      }
    )

    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(
        data.message || 'Unable to fetch drives',
        'danger'
      )
      return
    }

    drives.value = data

  }
  catch (err) {

    console.error(err)

    messageStore.updateMessages(
      'Unable to connect to server.',
      'danger'
    )

  }
  finally {

    loading.value = false

  }

}

async function closeDrive(id) {

  if (!confirm('Close this placement drive?'))
    return

  try {

    const res = await fetch(

      `http://127.0.0.1:5000/api/company/drives/${id}/close`,

      {
        method: 'PUT',

        headers: {
          Authorization: authStore.token
        }

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

    fetchDrives()

  }

  catch (err) {

    console.error(err)

    messageStore.updateMessages(
      'Server Error',
      'danger'
    )

  }

}

function createDrive() {

  router.push('/company/placement-drives/new')

}

function viewDrive(id) {

  router.push(`/company/placement-drives/${id}`)

}

onMounted(fetchDrives)
</script>

<template>

<div class="container mt-4">

  <div class="d-flex justify-content-between align-items-center mb-4">

    <h2>
      Placement Drives
    </h2>

    <button
      class="btn btn-success"
      @click="createDrive">

      + Create Drive

    </button>

  </div>

  <div class="card mb-4">

    <div class="card-body">

      <div class="row g-2">

        <div class="col-md-3">

          <input
            class="form-control"
            placeholder="Job Title"
            v-model="search.job_title">

        </div>

        <div class="col-md-2">

          <select
            class="form-select"
            v-model="search.status">

            <option value="">
              All Status
            </option>

            <option>
              Pending
            </option>

            <option>
              Approved
            </option>

            <option>
              Closed
            </option>

            <option>
              Rejected
            </option>

          </select>

        </div>

        <div class="col-md-2">

          <input
            type="date"
            class="form-control"
            v-model="search.start_date">

        </div>

        <div class="col-md-2">

          <input
            type="date"
            class="form-control"
            v-model="search.end_date">

        </div>

        <div class="col-md-3">

          <button
            class="btn btn-primary w-100"
            @click="fetchDrives">

            Search

          </button>

        </div>

      </div>

    </div>

  </div>

  <div
    v-if="loading"
    class="text-center">

    <div class="spinner-border"></div>

  </div>

  <table
    v-else
    class="table table-bordered table-hover">

    <thead class="table-dark">

      <tr>

        <th>ID</th>

        <th>Job Title</th>

        <th>Deadline</th>

        <th>Status</th>

        <th>Applications</th>

        <th width="180">
          Actions
        </th>

      </tr>

    </thead>

    <tbody>

      <tr
        v-for="drive in drives"
        :key="drive.id">

        <td>

          {{ drive.id }}

        </td>

        <td>

          {{ drive.job_title }}

        </td>

        <td>

          {{ drive.deadline }}

        </td>

        <td>

          <span
            class="badge"
            :class="{

              'bg-warning text-dark': drive.status=='Pending',

              'bg-success': drive.status=='Approved',

              'bg-danger': drive.status=='Rejected',

              'bg-secondary': drive.status=='Closed'

            }">

            {{ drive.status }}

          </span>

        </td>

        <td>

          {{ drive.applications }}

        </td>

        <td>

          <button
            class="btn btn-info btn-sm me-2"
            @click="viewDrive(drive.id)">

            View

          </button>

          <button
            class="btn btn-danger btn-sm"
            @click="closeDrive(drive.id)"
            :disabled="drive.status=='Closed' || drive.status=='Rejected'">

            Close

          </button>

        </td>

      </tr>

      <tr
        v-if="drives.length==0">

        <td
          colspan="6"
          class="text-center">

          No placement drives found.

        </td>

      </tr>

    </tbody>

  </table>

</div>

</template>