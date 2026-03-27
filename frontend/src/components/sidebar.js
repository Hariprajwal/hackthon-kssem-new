import React from 'react';
import { Folder, File, ChevronDown, Plus, FolderPlus, FileCode, FileText } from 'lucide-react';
import './sidebar.css';

const Sidebar = ({ explorerData, onFileSelect, onNewFile, onNewFolder, activeFileId }) => {
  const { folders = [], orphan_files = [] } = explorerData;

  const getFileIcon = (name) => {
    if (name.endsWith('.py')) return <FileCode size={14} color="#3776ab" />;
    if (name.endsWith('.js')) return <FileCode size={14} color="#f7df1e" />;
    if (name.endsWith('.txt')) return <FileText size={14} />;
    return <File size={14} />;
  };

  return (
    <div className="file-explorer">
      <div className="explorer-header">
        <span>EXPLORER</span>
        <div className="header-actions">
          <Plus size={16} onClick={onNewFile} className="action-icon" title="New File" />
          <FolderPlus size={16} onClick={onNewFolder} className="action-icon" title="New Folder" />
        </div>
      </div>

      <div className="explorer-content">
        {folders.map(folder => (
          <div key={folder.id} className="folder-item">
            <div className="item-label folder">
              <ChevronDown size={14} />
              <Folder size={14} fill="var(--primary)" color="var(--primary)" />
              <span>{folder.name}</span>
            </div>
            <div className="folder-children">
              {folder.files.map(file => (
                <div 
                  key={file.id} 
                  className={`item-label file ${activeFileId === file.id ? 'active' : ''}`}
                  onClick={() => onFileSelect(file)}
                >
                  {getFileIcon(file.name)}
                  <span>{file.name}</span>
                </div>
              ))}
            </div>
          </div>
        ))}

        {orphan_files.map(file => (
          <div 
            key={file.id} 
            className={`item-label file ${activeFileId === file.id ? 'active' : ''}`}
            onClick={() => onFileSelect(file)}
          >
            {getFileIcon(file.name)}
            <span>{file.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;
