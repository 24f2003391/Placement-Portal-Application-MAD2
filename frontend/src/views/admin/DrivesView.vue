<script setup>
import { ref, onMounted } from 'vue'
import { useMessageStore } from '@/stores/message'
import { useAuthStore } from '@/stores/auth'
import { useRoute, useRouter } from 'vue-router'
 
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const messageStore = useMessageStore()

const drives = ref([])
const loading = ref(false)

const selectedDrive = ref(null)
const showModal = ref(false)
const loadingDetails = ref(false)

const search = ref({
  company_id: route.query.company_id || '',
  job_title: '',
  status: '',
  start_date: '',
  end_date: ''
})

// 🔹 Open modal + lazy fetch
async function openDetails(id) {
  selectedDrive.value = null
  showModal.value = true
  loadingDetails.value = true

  try {
    const res = await fetch(`http://127.0.0.1:5000/api/admin/drive-details/${id}`,{
      method:"GET",
      headers:{
        "Content-Type": 'application/json',
        Authorization: authStore.token,
      }})
    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message || 'Failed to load details', 'danger')
      closeModal()
      return
    }

    selectedDrive.value = data

  } catch (err) {
    messageStore.updateMessages('Error loading details', 'danger')
    closeModal()
    console.error(err)
  } finally {
    loadingDetails.value = false
  }
}

// 🔹 Close modal cleanly
function closeModal() {
  showModal.value = false
  selectedDrive.value = null
}

// 🔹 Navigate to applications
function viewApplications(driveId) {
  router.push({
    path: '/admin/applications',
    query: {
        drive_id: driveId
    }
})
}

// 🔹 Fetch drives
async function fetchDrives() {
  loading.value = true
  try {
    const params = new URLSearchParams()

    Object.entries(search.value).forEach(([key, value]) => {
      if (value) params.append(key, value)
    })

    const res = await fetch(`http://127.0.0.1:5000/api/admin/drives?${params}`,{
      method:"GET",
      headers:{
        "Content-Type": 'application/json',
        Authorization: authStore.token,
      }})
    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message || 'Failed to fetch drives', 'danger')
      return
    }

    drives.value = data

  } catch (err) {
    messageStore.updateMessages('Error fetching drives', 'danger')
    console.error(err)
  } finally {
    loading.value = false
  }
}

// 🔹 Approve / Reject
async function performAction(id, action) {
  try {
    const res = await fetch(
      `http://127.0.0.1:5000/api/admin/drives/${id}/${action}`,{
      method:"PUT",
      headers:{
        "Content-Type": 'application/json',
        Authorization: authStore.token,
      }}
    )

    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message, 'danger')
      return
    }

    messageStore.updateMessages(data.message, 'success')
    fetchDrives()

  } catch (err) {
    messageStore.updateMessages('Action failed', 'danger')
    console.error(err)
  }
}

onMounted(fetchDrives)
</script>

<template>
  <div class="container mt-4">

    <h2 class="mb-3">Placement Drives</h2>

    <!-- ✅ MESSAGE DISPLAY (NO computed used) -->
    <div v-if="messageStore.messages.text" class="text-center mb-3">
      <div :class="`alert alert-${messageStore.messages.type}`">
        {{ messageStore.messages.text }}
      </div>
    </div>

    <!-- 🔍 Search -->
    <div class="row g-2 mb-3">
      <div class="col">
        <input v-model="search.company_id" class="form-control" placeholder="Company ID">
      </div>

      <div class="col">
        <input v-model="search.job_title" class="form-control" placeholder="Job Title">
      </div>

      <div class="col">
        <input type="date" v-model="search.start_date" class="form-control">
      </div>

      <div class="col">
        <input type="date" v-model="search.end_date" class="form-control">
      </div>

      <div class="col">
        <select v-model="search.status" class="form-select">
          <option value="">All Status</option>
          <option>Pending</option>
          <option>Approved</option>
          <option>Closed</option>
          <option>Rejected</option>
        </select>
      </div>

      <div class="col">
        <button class="btn btn-primary w-100" @click="fetchDrives">
          Search
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center">Loading...</div>

    <!-- Table -->
    <table v-if="!loading" class="table table-bordered table-hover">
      <!-- (unchanged below) -->
      <thead class="table-dark">
        <tr>
          <th>ID</th>
          <th>Company</th>
          <th>Job Title</th>
          <th>Deadline</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="d in drives" :key="d.id">
          <td>{{ d.id }}</td>
          <td>{{ d.company_id }}</td>
          <td>{{ d.job_title }}</td>
          <td>{{ d.application_deadline }}</td>

          <td>
            <span :class="{
              'badge bg-warning text-dark': d.status === 'Pending',
              'badge bg-success': d.status === 'Approved',
              'badge bg-danger': d.status === 'Rejected',
              'badge bg-secondary': d.status === 'Closed'
            }">
              {{ d.status }}
            </span>
          </td>

          <td>
            <button class="btn btn-info btn-sm me-2"
              :disabled="loadingDetails"
              @click="openDetails(d.id)">
              View Details
            </button>

            <div v-if="d.status === 'Pending'">
              <button class="btn btn-success btn-sm me-2"
                @click="performAction(d.id, 'approve')">
                Approve
              </button>

              <button class="btn btn-danger btn-sm"
                @click="performAction(d.id, 'reject')">
                Reject
              </button>
            </div>

            <div v-else-if="d.status === 'Approved'">
              <button class="btn btn-primary btn-sm"
                @click="viewApplications(d.id)">
                View Applications
              </button>
            </div>

            <div v-else>
              <span class="text-muted">No actions</span>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 🔥 MODAL -->
    <div class="modal fade show d-block" v-if="showModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">

          <!-- Header -->
          <div class="modal-header">
            <h5 class="modal-title">
              {{ selectedDrive?.job_title || 'Loading...' }}
            </h5>
            <button class="btn-close" @click="closeModal"></button>
          </div>

          <!-- Body -->
          <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">

            <!-- Spinner -->
            <div v-if="loadingDetails" class="text-center my-3">
              <div class="spinner-border"></div>
            </div>

            <!-- Content -->
            <div v-else-if="selectedDrive">

              <h6>Job Description</h6>
              <p>{{ selectedDrive.job_description }}</p>

              <h6>Eligibility</h6>

              <div v-if="selectedDrive.eligibility.length === 0" class="text-muted">
                No eligibility criteria defined
              </div>

              <table v-else class="table table-sm table-bordered">
                <thead>
                  <tr>
                    <th>Program</th>
                    <th>Min CGPA</th>
                    <th>Year</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="e in selectedDrive.eligibility" :key="e.id">
                    <td>{{ e.program }}</td>
                    <td>{{ e.min_cgpa }}</td>
                    <td>{{ e.year }}</td>
                  </tr>
                </tbody>
              </table>

            </div>

          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeModal">
              Close
            </button>
          </div>

        </div>
      </div>
    </div>

    <!-- Backdrop -->
    <div class="modal-backdrop fade show" v-if="showModal"></div>

  </div>
</template>