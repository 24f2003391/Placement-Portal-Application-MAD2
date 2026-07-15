<script setup>
import { ref, onMounted } from 'vue'
import { useMessageStore } from '@/stores/message'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()

const messageStore = useMessageStore()
const authStore=useAuthStore()

const students = ref([])
const loading = ref(false)

const showPlacementModal = ref(false)
const loadingPlacement = ref(false)

const placement = ref(null)

const programs = ref([]);

function viewApplications(roll_no) {
  router.push({
    path: '/admin/applications',   
    query: { student_id: roll_no }
  })
}
async function viewPlacement(roll_no) {

  placement.value = null
  showPlacementModal.value = true
  loadingPlacement.value = true

  try {

    const res = await fetch(
      `http://127.0.0.1:5000/api/admin/students/${roll_no}/placement`,
      {
        headers: {
          Authorization: authStore.token
        }
      }
    )

    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(
        data.message || 'Failed to load placement details',
        'danger'
      )

      closePlacementModal()
      return
    }

    placement.value = data

  }
  catch (err) {

    console.error(err)

    messageStore.updateMessages(
      'Error loading placement details',
      'danger'
    )

    closePlacementModal()
  }
  finally {
    loadingPlacement.value = false
  }

}
function closePlacementModal() {
  placement.value = null
  showPlacementModal.value = false
}
async function downloadOffer() {

  try {

    const res = await fetch(
      `http://127.0.0.1:5000/api/admin/offers/${placement.value.offer.offer_id}/download`,
      {
        headers: {
          Authorization: authStore.token
        }
      }
    )

    if (!res.ok) {
      messageStore.updateMessages(
        "Couldn't download offer letter",
        "danger"
      )
      return
    }

    const blob = await res.blob()

    const url = URL.createObjectURL(blob)

    const a = document.createElement('a')
    a.href = url
    a.download = ''
    a.click()

    URL.revokeObjectURL(url)

  }
  catch (err) {

    console.error(err)

    messageStore.updateMessages(
      "Error downloading offer letter",
      "danger"
    )

  }

}

onMounted(async () => {
  try {
    const res = await fetch('http://127.0.0.1:5000/api/programs')
    const data = await res.json()
    programs.value = data
  } catch (err) {
    console.error('Failed to load programs', err)
    messageStore.updateMessages(
    "Failed to load programs",
    "danger"
)
  }
})

const search = ref({
  name: '',
  roll_no: '',
  phone: '',
  program:'',
  is_blacklisted: '',
  placed:''
})

async function fetchStudents() {
  loading.value = true
  try {
    const params = new URLSearchParams()

    Object.entries(search.value).forEach(([key, value]) => {
      if (value !== '' && value !== null) {
        params.append(key, value)
      }
    })

    const res = await fetch(`http://127.0.0.1:5000/api/admin/students?${params}`,{
      method: 'GET',
      headers:{
        "Content-Type": 'application/json',
        Authorization: authStore.token,
      }})
    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message || 'Failed to fetch students', 'danger')
      return
    }

    students.value = data

  } catch (err) {
    messageStore.updateMessages('Something went wrong while fetching students', 'danger')
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function performAction(roll_no, action) {
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/admin/students/${roll_no}/${action}`, {
      method: 'PUT',
      headers:{
          "Content-Type": 'application/json',
          Authorization: authStore.token,
      }
    })
    const data = await res.json()
    if (!res.ok) {
      messageStore.updateMessages(data.message || 'Action failed', 'danger')
      return
    }

    messageStore.updateMessages(data.message, 'success')
    await fetchStudents()

  } catch (err) {
    messageStore.updateMessages('Something went wrong while performing action', 'danger')
    console.error(err)
  }
}

onMounted(fetchStudents)
</script>

<template>
  <div class="container mt-4">

    <!-- 🔍 Search -->
    <div class="row g-2 mb-3">
      
      <div class="col">
        <input v-model="search.name" class="form-control" placeholder="Name">
      </div>

      <div class="col">
        <input v-model="search.roll_no" class="form-control" placeholder="Roll No" type="number">
      </div>

      <div class="col">
        <input v-model="search.phone" class="form-control" placeholder="Phone">
      </div>

      <div class="mb-3">
            <label for="program" class="form-label">Program</label>
            <select 
                id="program"
                class="form-select"
                v-model="search.program">
                <option value="">All Programs</option>
                <option 
                v-for="prog in programs" 
                :key="prog.code" 
                :value="prog.code"
                >
                {{ prog.name }} ({{ prog.code }})
                </option>
            </select>
        </div>

      <div class="col">
        <select v-model="search.is_blacklisted" class="form-select">
          <option value="">Blacklist(yes/no)</option>
          <option value="true">Blacklisted</option>
          <option value="false">Active</option>
        </select>
      </div>
      </div class="col">
        <select v-model="search.placed" class="form-select">
          <option value="">Placement Status</option>
          <option value="true">Placed</option>
          <option value="false">Not Placed</option>
      </select>
      </div>

      <div class="col">
        <button class="btn btn-primary w-100" @click="fetchStudents">
          Search
        </button>
      </div>

    <div>

    <div v-if="loading" class="text-center">
      Loading...
    </div>

    <table v-if="!loading" class="table table-bordered table-hover">
      <thead class="table-dark">
        <tr>
          <th>Roll No</th>
          <th>Name</th>
          <th>Phone</th>
          <th>Program</th>
          <th>CGPA</th>
          <th>Year</th>
          <th>Placed</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="s in students" :key="s.roll_no">
          <td>{{ s.roll_no }}</td>
          <td>{{ s.name }}</td>
          <td>{{ s.phone_no }}</td>
          <td>{{ s.program_name }}</td>
          <td>{{ s.cgpa }}</td>
          <td>{{ s.year_in_program }}</td>
          <td>
              <span
                  :class="s.placed
                      ? 'badge bg-success'
                      : 'badge bg-secondary'">

                  {{ s.placed ? 'Placed' : 'Not Placed' }}

              </span>
          </td>
          <td>
            <button class="btn btn-info btn-sm me-2"
                @click="viewApplications(s.roll_no)">
                View Applications
            </button>

            <button class="btn btn-warning btn-sm me-2"
              v-if="!s.is_blacklisted"
              @click="performAction(s.roll_no, 'blacklist')">
              Blacklist
            </button>

            <button class="btn btn-secondary btn-sm"
              v-if="s.is_blacklisted"
              @click="performAction(s.roll_no, 'unblacklist')">
              Unblacklist
            </button>
            <button
              v-if="s.placed"
              class="btn btn-success btn-sm me-2"
              @click="viewPlacement(s.roll_no)">
              Placement Details
          </button>

          </td>

        </tr>
      </tbody>
    </table>
    <!-- Placement Details Modal -->
<div class="modal fade show d-block" v-if="showPlacementModal">
  <div class="modal-dialog">
    <div class="modal-content">

      <div class="modal-header">
        <h5 class="modal-title">Placement Details</h5>
        <button class="btn-close" @click="closePlacementModal"></button>
      </div>

      <div class="modal-body">

        <div v-if="loadingPlacement" class="text-center">
          <div class="spinner-border"></div>
        </div>

        <div v-else-if="placement">

          <table class="table table-bordered">
           <tbody>

            <tr>
              <th>Company</th>
              <td>{{ placement.application.company }}</td>
            </tr>

            <tr>
              <th>Job Title</th>
              <td>{{ placement.application.job_title }}</td>
            </tr>

            <tr>
              <th>Role</th>
              <td>{{ placement.offer.job_role }}</td>
            </tr>

            <tr>
              <th>Package</th>
              <td>{{ placement.offer.package }}</td>
            </tr>

            <tr>
              <th>Joining Date</th>
              <td>{{ placement.offer.joining_date }}</td>
            </tr>

            <tr>
              <th>Status</th>
              <td>{{ placement.offer.status }}</td>
            </tr>
            </tbody>

          </table>

        </div>

      </div>

      <div class="modal-footer">

        <button class="btn btn-primary"
                @click="downloadOffer">
          Download Offer Letter
        </button>

        <button class="btn btn-secondary"
                @click="closePlacementModal">
          Close
        </button>

      </div>

    </div>
  </div>
</div>

<div class="modal-backdrop fade show" v-if="showPlacementModal"></div>
  </div>
</template>