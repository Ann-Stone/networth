import { ElMessageBox } from 'element-plus'

export type ConfirmType = 'warning' | 'info' | 'error'

export interface ConfirmOptions {
  title: string
  message: string
  type?: ConfirmType
}

export function useConfirm() {
  return async (opts: ConfirmOptions): Promise<boolean> => {
    try {
      await ElMessageBox.confirm(opts.message, opts.title, {
        confirmButtonText: '確認',
        cancelButtonText: '取消',
        type: opts.type ?? 'warning',
      })
      return true
    } catch {
      return false
    }
  }
}
