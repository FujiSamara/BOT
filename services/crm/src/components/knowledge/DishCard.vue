<script setup lang="ts">
import { PropType } from "vue";
import { KnowledgeCard } from "@/components/knowledge";

const props = defineProps({
	card: {
		type: Object as PropType<KnowledgeCard>,
		required: true,
	},
});
</script>
<template>
	<div class="dish-card"></div>
</template>
<style scoped lang="scss"></style>
