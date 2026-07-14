```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'

const route = useRoute()

const authStore = useAuthStore()
const messageStore = useMessageStore()

const loading = ref(false)

const offer = ref({
  student_name: '',
  roll_no: '',
  program: '',
  job_role: '',
  package: '',
  joining_date: '',
  status: ''
})

async function fetchOffer() {

  loading.value = true

  try {

    const res = await fetch(
      `http://127.0.0.1:5000/api/company/offers/${route.params.offer_id}`,
      {
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

    offer.value = data

  }
  catch (err) {

    console.error(err)

    messageStore.updateMessages(
      'Unable to fetch offer details.',
      'danger'
    )

  }
  finally {

    loading.value = false

  }

}

onMounted(fetchOffer)
</script>

<template>

<div class="container mt-4">

  <div
    v-if="loading"
    class="text-center my-5">

    <div class="spinner-border"></div>

  </div>

  <div
    v-else
    class="card">

    <div class="card-header">

      <h4 class="mb-0">
        Offer Details
      </h4>

    </div>

    <div class="card-body">

      <div class="row mb-3">

        <div class="col-md-6">
          <strong>Student</strong>
          <p>{{ offer.student_name }}</p>
        </div>

        <div class="col-md-6">
          <strong>Roll Number</strong>
          <p>{{ offer.roll_no }}</p>
        </div>

      </div>

      <div class="row mb-3">

        <div class="col-md-6">
          <strong>Program</strong>
          <p>{{ offer.program }}</p>
        </div>

        <div class="col-md-6">
          <strong>Job Role</strong>
          <p>{{ offer.job_role }}</p>
        </div>

      </div>

      <div class="row mb-3">

        <div class="col-md-6">
          <strong>Package</strong>
          <p>{{ offer.package }} LPA</p>
        </div>

        <div class="col-md-6">
          <strong>Joining Date</strong>
          <p>{{ offer.joining_date }}</p>
        </div>

      </div>

      <div>

        <strong>Status</strong>

        <div class="mt-2">

          <span
            class="badge"
            :class="{
              'bg-warning text-dark': offer.status === 'Offered',
              'bg-success': offer.status === 'Accepted',
              'bg-danger': offer.status === 'Rejected'
            }">

            {{ offer.status }}

          </span>

        </div>

      </div>

    </div>

  </div>

</div>

</template>
```
