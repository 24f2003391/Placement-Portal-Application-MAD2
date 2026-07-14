<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'

const router = useRouter()

const authStore = useAuthStore()
const messageStore = useMessageStore()

const loading = ref(false)

const company = ref({})
const statistics = ref({})
const recentDrives = ref([])

async function fetchDashboard() {
  loading.value = true

  try {
    const res = await fetch(
      'http://127.0.0.1:5000/api/company/dashboard',
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
        data.message || 'Failed to load dashboard',
        'danger'
      )
      return
    }

    company.value = data.company
    statistics.value = data.statistics
    recentDrives.value = data.recent_drives

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

// function createDrive() {
//   router.push('/company/placement-drives/new')
// }

// function manageDrives() {
//   router.push('/company/placement-drives')
// }

function viewDrive(id) {
  router.push(`/company/placement-drives/${id}`)
}

onMounted(fetchDashboard)
</script>

<template>
<div class="container mt-4">

  <div class="d-flex justify-content-between align-items-center mb-4">

    <div>
      <h2>Welcome, {{ company.name }}</h2>
      <p class="text-muted mb-0">
        Company Dashboard
      </p>
    </div>

    <!-- <div>

      <button
        class="btn btn-success me-2"
        @click="createDrive">

        + Create Placement Drive

      </button>

      <button
        class="btn btn-primary"
        @click="manageDrives">

        Manage Drives

      </button>

    </div> -->

  </div>

  <div
    v-if="loading"
    class="text-center mt-5">

    <div class="spinner-border"></div>

  </div>

  <template v-else>

    <div class="row">

      <div class="col-md-3 mb-3">

        <div class="card shadow-sm text-center">

          <div class="card-body">

            <h2>{{ statistics.total_drives }}</h2>

            <p class="mb-0">
              Total Drives
            </p>

          </div>

        </div>

      </div>

      <div class="col-md-3 mb-3">

        <div class="card shadow-sm text-center">

          <div class="card-body">

            <h2>{{ statistics.active_drives }}</h2>

            <p class="mb-0">
              Active Drives
            </p>

          </div>

        </div>

      </div>

      <div class="col-md-3 mb-3">

        <div class="card shadow-sm text-center">

          <div class="card-body">

            <h2>{{ statistics.total_applications }}</h2>

            <p class="mb-0">
              Applications
            </p>

          </div>

        </div>

      </div>

      <div class="col-md-3 mb-3">

        <div class="card shadow-sm text-center">

          <div class="card-body">

            <h2>{{ statistics.selected }}</h2>

            <p class="mb-0">
              Selected
            </p>

          </div>

        </div>

      </div>

    </div>

    <div class="card shadow-sm mt-4">

      <div class="card-header d-flex justify-content-between">

        <strong>Recent Placement Drives</strong>

      </div>

      <div class="card-body">

        <table class="table table-hover align-middle">

          <thead>

            <tr>

              <th>ID</th>
              <th>Job Title</th>
              <th>Deadline</th>
              <th>Status</th>
              <th>Applications</th>
              <th>Action</th>

            </tr>

          </thead>

          <tbody>

            <tr
              v-for="drive in recentDrives"
              :key="drive.id">

              <td>{{ drive.id }}</td>

              <td>{{ drive.job_title }}</td>

              <td>{{ drive.deadline }}</td>

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
                  class="btn btn-sm btn-outline-primary"
                  @click="viewDrive(drive.id)">

                  View

                </button>

              </td>

            </tr>

            <tr
              v-if="recentDrives.length===0">

              <td
                colspan="6"
                class="text-center">

                No Placement Drives Yet

              </td>

            </tr>

          </tbody>

        </table>

      </div>

    </div>

  </template>

</div>
</template>