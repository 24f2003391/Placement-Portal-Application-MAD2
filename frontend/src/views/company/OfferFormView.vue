```vue
<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'

const route = useRoute()
const router = useRouter()

const authStore = useAuthStore()
const messageStore = useMessageStore()

const loading = ref(false)

const form = ref({
  job_role: '',
  package: '',
  joining_date: '',
  offer_letter: null
})

function handleFileChange(event) {
  form.value.offer_letter = event.target.files[0]
}

async function submitOffer() {

  if (
    !form.value.job_role ||
    !form.value.package ||
    !form.value.joining_date ||
    !form.value.offer_letter
  ) {
    messageStore.updateMessages(
      'All fields are required.',
      'warning'
    )
    return
  }

  loading.value = true

  try {

    const formData = new FormData()

    formData.append('job_role', form.value.job_role)
    formData.append('package', form.value.package)
    formData.append('joining_date', form.value.joining_date)
    formData.append('offer_letter', form.value.offer_letter)

    const res = await fetch(
      `http://127.0.0.1:5000/api/company/applications/${route.params.application_id}/offer`,
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

    messageStore.updateMessages(data.message)

    router.replace(`/company/offers/${data.offer_id}`)

  } catch (err) {

    console.error(err)

    messageStore.updateMessages(
      'Unable to issue offer.',
      'danger'
    )

  } finally {

    loading.value = false

  }

}
</script>

<template>

<div class="container mt-4">

  <div class="row justify-content-center">

    <div class="col-lg-8">

      <div class="card">

        <div class="card-header">
          <h4 class="mb-0">
            Issue Offer
          </h4>
        </div>

        <div class="card-body">

          <div class="mb-3">

            <label class="form-label">
              Job Role
            </label>

            <input
              type="text"
              class="form-control"
              v-model="form.job_role"
            >

          </div>

          <div class="mb-3">

            <label class="form-label">
              Package (LPA)
            </label>

            <input
              type="number"
              step="0.01"
              min="0"
              class="form-control"
              v-model="form.package"
            >

          </div>

          <div class="mb-3">

            <label class="form-label">
              Joining Date
            </label>

            <input
              type="date"
              class="form-control"
              v-model="form.joining_date"
            >

          </div>

          <div class="mb-4">

            <label class="form-label">
              Offer Letter (PDF)
            </label>

            <input
              type="file"
              class="form-control"
              accept=".pdf,application/pdf"
              @change="handleFileChange"
            >

          </div>

        </div>

        <div class="card-footer text-end">

          <button
            class="btn btn-secondary me-2"
            @click="router.back()"
            :disabled="loading"
          >
            Cancel
          </button>

          <button
            class="btn btn-primary"
            @click="submitOffer"
            :disabled="loading"
          >
            {{ loading ? 'Issuing Offer...' : 'Issue Offer' }}
          </button>

        </div>

      </div>

    </div>

  </div>

</div>

</template>
```
