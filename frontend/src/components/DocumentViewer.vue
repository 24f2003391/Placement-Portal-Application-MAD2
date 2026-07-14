<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-centered">
      <div class="modal-content">

        <!-- Header -->
        <div class="modal-header">
          <h5 class="modal-title">{{ title }}</h5>
          <button type="button" class="btn-close" @click="close"></button>
        </div>

        <!-- Body -->
        <div class="modal-body">

          <!-- PDF Viewer -->
          <iframe
              v-if="pdfUrl"
              :src="pdfUrl"
              class="w-100 mb-3"
              height="400">
          </iframe>

          <!-- Download Button -->
          <div class="d-flex justify-content-end mb-3">
            <a
                v-if="pdfUrl"
                :href="pdfUrl"
                class="btn btn-primary"
                download>
                Download PDF
            </a>
          </div>

          <!-- Key-Value Table -->
          <table class="table table-bordered table-sm">
            <tbody>
              <tr v-for="(value, key) in details" :key="key">
                <th class="w-25">{{ key }}</th>
                <td>{{ value }}</td>
              </tr>
            </tbody>
          </table>

        </div>

      </div>
    </div>
  </div>

  <!-- Backdrop (Bootstrap style) -->
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>

<script setup>
defineProps({
  show: Boolean,
  title: String,
  pdfUrl: String,
  details: Object
})

const emit = defineEmits(['close'])

function close() {
  emit('close')
}
</script>